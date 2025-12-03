import sys
import os
import json
import time
import threading
import asyncio
from unittest.mock import MagicMock

# Mock dependencies
sys.modules["numpy"] = MagicMock()
sys.modules["pydantic"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["src.bridge_api.event_bus"] = MagicMock()
sys.modules["src.bridge_api.ai_shield.state"] = MagicMock()
sys.modules["src.bridge_api.telemetry.thermo"] = MagicMock()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.scf.daemon.scf_daemon import SCFSovereignDaemon

def test_daemon_integration():
    print("🧪 Testing SCF Sovereign Daemon Integration...")
    
    # Clean up stale control file
    if os.path.exists("data/scf/control.json"):
        os.remove("data/scf/control.json")

    # Initialize Daemon
    daemon = SCFSovereignDaemon()
    
    # Mock internal components to avoid real execution
    # We need to set the result on the future in the loop where it's awaited, 
    # but for this simple test we can just return a completed future.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.Future()
    future.set_result({"status": "deployed", "intent": "Test Intent"})
    daemon.master_loop.cycle = MagicMock(return_value=future)
    
    # Start Daemon in a separate thread
    daemon_thread = threading.Thread(target=daemon.start)
    daemon_thread.start()
    
    time.sleep(1) # Wait for startup
    
    try:
        # 1. Verify Heartbeat
        assert os.path.exists(daemon.heartbeat_file)
        with open(daemon.heartbeat_file, 'r') as f:
            heartbeat = json.load(f)
        print(f"✅ Heartbeat detected. Status: {heartbeat['status']}, Level: {heartbeat['level']}")
        assert heartbeat['status'] == "RUNNING"
        assert heartbeat['level'] == "STANDARD"
        
        # 2. Send Control Command (Shift Gear)
        control_cmd = {
            "command": "SHIFT_GEAR",
            "payload": {"level": "ACCELERATED"}
        }
        with open(daemon.control_file, 'w') as f:
            json.dump(control_cmd, f)
            
        print("📤 Sent SHIFT_GEAR command...")
        time.sleep(6) # Wait for processing (Daemon sleeps 5s in STANDARD)
        
        # 3. Verify Level Change
        with open(daemon.heartbeat_file, 'r') as f:
            heartbeat = json.load(f)
        print(f"✅ Heartbeat updated. Level: {heartbeat['level']}")
        assert heartbeat['level'] == "ACCELERATED"
        
        # 4. Verify Loop Execution
        assert daemon.cycles_completed > 0
        print(f"✅ Cycles Completed: {daemon.cycles_completed}")
        
    finally:
        # Stop Daemon
        daemon.stop()
        daemon_thread.join()
        print("🛑 Daemon Stopped.")

if __name__ == "__main__":
    test_daemon_integration()
