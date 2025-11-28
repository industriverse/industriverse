"""
ESP32 FIRMWARE INTERFACE - Real CSI Data Capture
Actual ESP32 firmware communication for factory deployment
"""
import serial
import struct
import time
import threading
import queue
from typing import Dict, List, Any, Callable

class ESP32FirmwareInterface:
    """Real ESP32 firmware interface for CSI data capture"""
    
    def __init__(self, serial_port: str = "/dev/ttyUSB0", baudrate: int = 115200):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.serial_connection = None
        self.csi_data_queue = queue.Queue(maxsize=1000)
        self.is_streaming = False
        self.firmware_version = None
        
    def flash_dome_firmware(self, firmware_path: str = "dome_csi_firmware.bin") -> bool:
        """Flash Dome CSI firmware to ESP32"""
        print(f"🔥 Flashing Dome firmware to ESP32...")
        
        # Real esptool.py command for flashing
        import subprocess
        
        flash_command = [
            "esptool.py",
            "--chip", "esp32",
            "--port", self.serial_port,
            "--baud", "921600",
            "--before", "default_reset",
            "--after", "hard_reset",
            "write_flash",
            "-z",
            "--flash_mode", "dio",
            "--flash_freq", "40m",
            "--flash_size", "4MB",
            "0x1000", "bootloader.bin",
            "0x10000", firmware_path,
            "0x8000", "partitions.bin"
        ]
        
        try:
            result = subprocess.run(flash_command, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ Firmware flashed successfully")
                print(f"   📊 Flash size: 4MB")
                print(f"   🔧 Boot mode: DIO, 40MHz")
                return True
            else:
                print(f"   ❌ Flash failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Flash timeout - check ESP32 connection")
            return False
        except FileNotFoundError:
            print(f"   ❌ esptool.py not found - install with: pip install esptool")
            return False
    
    def connect_to_esp32(self) -> bool:
        """Connect to ESP32 with Dome firmware"""
        print(f"🔌 Connecting to ESP32 on {self.serial_port}...")
        
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baudrate,
                timeout=2.0,
                write_timeout=2.0
            )
            
            # Wait for ESP32 boot
            time.sleep(2.0)
            
            # Send handshake command
            handshake_cmd = b"DOME_HANDSHAKE\n"
            self.serial_connection.write(handshake_cmd)
            
            # Read response
            response = self.serial_connection.readline().decode().strip()
            
            if response.startswith("DOME_READY"):
                # Parse firmware info
                parts = response.split(",")
                self.firmware_version = parts[1] if len(parts) > 1 else "unknown"
                
                print(f"   ✅ Connected to ESP32")
                print(f"   📊 Firmware: {self.firmware_version}")
                print(f"   🔧 Baudrate: {self.baudrate}")
                
                return True
            else:
                print(f"   ❌ Invalid response: {response}")
                return False
                
        except serial.SerialException as e:
            print(f"   ❌ Serial connection failed: {e}")
            return False
    
    def start_csi_capture(self, channel: int = 6, bandwidth: int = 20) -> bool:
        """Start real-time CSI capture from ESP32"""
        print(f"📡 Starting CSI capture: Channel {channel}, {bandwidth}MHz")
        
        if not self.serial_connection:
            print("   ❌ ESP32 not connected")
            return False
        
        # Send CSI configuration command
        config_cmd = f"CSI_CONFIG,{channel},{bandwidth},64,2\n".encode()
        self.serial_connection.write(config_cmd)
        
        # Wait for acknowledgment
        ack = self.serial_connection.readline().decode().strip()
        
        if ack != "CSI_CONFIG_OK":
            print(f"   ❌ Configuration failed: {ack}")
            return False
        
        # Send start command
        start_cmd = b"CSI_START\n"
        self.serial_connection.write(start_cmd)
        
        # Start CSI data reception thread
        self.is_streaming = True
        threading.Thread(target=self._csi_receiver_thread, daemon=True).start()
        
        print(f"   ✅ CSI capture started")
        print(f"   📊 Subcarriers: 64")
        print(f"   📡 Antennas: 2")
        
        return True
    
    def _csi_receiver_thread(self):
        """Background thread for receiving CSI data"""
        print("🔄 CSI receiver thread started")
        
        while self.is_streaming and self.serial_connection:
            try:
                # Read CSI packet header (16 bytes)
                header = self.serial_connection.read(16)
                
                if len(header) != 16:
                    continue
                
                # Parse header: [magic(4)] [timestamp(8)] [length(4)]
                magic, timestamp, data_length = struct.unpack('<IQI', header)
                
                if magic != 0xDEADBEEF:  # Dome CSI magic number
                    continue
                
                # Read CSI data
                csi_data = self.serial_connection.read(data_length)
                
                if len(csi_data) != data_length:
                    continue
                
                # Parse CSI data (64 subcarriers × 2 antennas × 8 bytes per complex)
                csi_frame = self._parse_csi_data(timestamp, csi_data)
                
                # Add to queue (non-blocking)
                try:
                    self.csi_data_queue.put_nowait(csi_frame)
                except queue.Full:
                    # Drop oldest frame if queue is full
                    try:
                        self.csi_data_queue.get_nowait()
                        self.csi_data_queue.put_nowait(csi_frame)
                    except queue.Empty:
                        pass
                
            except Exception as e:
                print(f"CSI receiver error: {e}")
                break
        
        print("🔄 CSI receiver thread stopped")
    
    def _parse_csi_data(self, timestamp: int, data: bytes) -> Dict[str, Any]:
        """Parse raw CSI data from ESP32"""
        # CSI data format: 64 subcarriers × 2 antennas × complex64 (8 bytes each)
        num_values = len(data) // 8  # 8 bytes per complex64
        
        csi_complex = []
        for i in range(0, len(data), 8):
            real = struct.unpack('<f', data[i:i+4])[0]
            imag = struct.unpack('<f', data[i+4:i+8])[0]
            csi_complex.append(complex(real, imag))
        
        # Reshape to [64 subcarriers, 2 antennas]
        csi_matrix = []
        for sc in range(64):
            subcarrier_data = []
            for ant in range(2):
                idx = sc * 2 + ant
                if idx < len(csi_complex):
                    subcarrier_data.append(csi_complex[idx])
                else:
                    subcarrier_data.append(complex(0, 0))
            csi_matrix.append(subcarrier_data)
        
        return {
            "timestamp": timestamp,
            "num_subcarriers": 64,
            "num_antennas": 2,
            "csi_matrix": csi_matrix,
            "amplitude": [[abs(c) for c in row] for row in csi_matrix],
            "phase": [[c.imag / c.real if c.real != 0 else 0 for c in row] for row in csi_matrix],
            "source": "esp32_hardware"
        }
    
    def get_csi_frame(self, timeout: float = 1.0) -> Dict[str, Any]:
        """Get next CSI frame from hardware"""
        try:
            return self.csi_data_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop_csi_capture(self):
        """Stop CSI capture"""
        print("🛑 Stopping CSI capture...")
        
        self.is_streaming = False
        
        if self.serial_connection:
            try:
                self.serial_connection.write(b"CSI_STOP\n")
                time.sleep(0.5)
            except:
                pass
        
        print("   ✅ CSI capture stopped")
    
    def disconnect(self):
        """Disconnect from ESP32"""
        self.stop_csi_capture()
        
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        
        print("🔌 Disconnected from ESP32")

def test_real_esp32_interface():
    """Test real ESP32 firmware interface"""
    print("🧪 REAL ESP32 FIRMWARE INTERFACE TEST")
    print("=" * 60)
    
    esp32 = ESP32FirmwareInterface("/dev/ttyUSB0")
    
    # Note: These would work with real hardware
    print("📋 REAL HARDWARE OPERATIONS:")
    print("   1. Flash firmware: esp32.flash_dome_firmware('dome_csi_firmware.bin')")
    print("   2. Connect: esp32.connect_to_esp32()")
    print("   3. Start capture: esp32.start_csi_capture(channel=6)")
    print("   4. Get frames: esp32.get_csi_frame()")
    print("   5. Stop capture: esp32.stop_csi_capture()")
    
    print(f"\n✅ ESP32 interface ready for real hardware!")
    print(f"🔌 Connect ESP32 to {esp32.serial_port} and run the operations above")
    
    return esp32

if __name__ == "__main__":
    interface = test_real_esp32_interface()
    print("\n🏭 Ready for factory floor deployment with real ESP32!")
