import h5py
import numpy as np
import os
import sys
import json
import time

class TelemetryLogger:
    """
    AI Shield v3 - Gate 5: Telemetry Logger.
    Persists real-time machine data to HDF5 for 'Shadow Twin' replay and analysis.
    """
    def __init__(self, buffer_path="telemetry_buffer.h5"):
        self.buffer_path = buffer_path
        
    def log_batch(self, machine_id, data_batch):
        """
        Input: machine_id (str), data_batch (list of dicts)
        """
        if not data_batch:
            return
            
        # Convert list of dicts to structured arrays
        timestamps = [d.get('timestamp', time.time()) for d in data_batch]
        temps = [d.get('temp', 0.0) for d in data_batch]
        vibrations = [d.get('vibration', 0.0) for d in data_batch]
        
        with h5py.File(self.buffer_path, 'a') as f:
            # Create Group for Machine if not exists
            if machine_id not in f:
                grp = f.create_group(machine_id)
                # Initialize Datasets (Resizable)
                grp.create_dataset('timestamp', data=timestamps, maxshape=(None,), chunks=True)
                grp.create_dataset('temp', data=temps, maxshape=(None,), chunks=True)
                grp.create_dataset('vibration', data=vibrations, maxshape=(None,), chunks=True)
            else:
                grp = f[machine_id]
                # Append Data
                self._append_dataset(grp, 'timestamp', timestamps)
                self._append_dataset(grp, 'temp', temps)
                self._append_dataset(grp, 'vibration', vibrations)
                
        return {"status": "logged", "count": len(data_batch)}

    def _append_dataset(self, group, name, new_data):
        dset = group[name]
        dset.resize(dset.shape[0] + len(new_data), axis=0)
        dset[-len(new_data):] = new_data

if __name__ == "__main__":
    # CLI Interface for Node.js
    if len(sys.argv) > 1:
        try:
            input_data = json.loads(sys.argv[1])
            machine_id = input_data.get("machine_id")
            batch = input_data.get("batch")
            
            logger = TelemetryLogger()
            result = logger.log_batch(machine_id, batch)
            print(json.dumps(result))
        except Exception as e:
            import traceback
            print(json.dumps({"error": str(e), "trace": traceback.format_exc()}))
