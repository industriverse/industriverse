import h5py
import sys
import os

# Check if buffer exists
buffer_path = "src/telemetry/telemetry_buffer.h5"
if not os.path.exists(buffer_path):
    # Try root if running from root
    buffer_path = "telemetry_buffer.h5" 
    # The logger writes to 'telemetry_buffer.h5' in CWD by default if not specified otherwise in constructor,
    # but the Hub calls it. Let's check where it wrote.
    # The Hub calls logger with default args, so it writes to CWD of the process.
    # Since we run node from root, it should be in root.

if not os.path.exists("telemetry_buffer.h5"):
    print("❌ HDF5 Buffer file not found.")
    sys.exit(1)

try:
    with h5py.File("telemetry_buffer.h5", 'r') as f:
        machine_id = "Test_Machine_001"
        if machine_id not in f:
            print(f"❌ Machine Group {machine_id} not found.")
            sys.exit(1)
            
        grp = f[machine_id]
        count = len(grp['temp'])
        print(f"Found {count} data points for {machine_id}.")
        
        if count == 10:
            print("✅ Data count matches (10).")
            print(f"Sample Temp: {grp['temp'][0]}")
        else:
            print(f"❌ Data count mismatch. Expected 10, got {count}")
            sys.exit(1)

except Exception as e:
    print(f"❌ Verification failed: {e}")
    sys.exit(1)
