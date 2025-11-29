# EDCoC Software Integration Map

## 1. The Edge Stack
The EDCoC runs a stripped-down, real-time version of the Industriverse OS.

### Layer 1: The Thermodynamic Kernel (RTOS)
- **Role**: Safety watchdog. Enforces MCM constraints at the millisecond level.
- **Input**: Real-time sensor data (Thermal, Force).
- **Action**: Emergency Stop if entropy exceeds safe bounds.

### Layer 2: The Local Data Hub
- **Role**: Buffers telemetry and simulation logs.
- **Process**: `CollectorDaemon` runs locally.
- **Sync**: Batches compressed shards to the Cloud Data Hub every 10 minutes (or real-time via 5G).

### Layer 3: Capsule Sandbox
- **Role**: Executes Capsules (Python/WASM).
- **Isolation**: Each Capsule runs in a secure container.
- **Verification**: ZK Proofs generated locally in the Secure Enclave.

### Layer 4: The A2A Mesh
- **Role**: Local P2P communication with other EDCoCs.
- **Protocol**: MQTT / DDS over Wi-Fi 6E.
- **Function**: Distributed bidding and skill sharing without cloud latency.

## 2. Cloud <-> Edge Sync
- **Downlink**: New Skills (PSSM), Global Energy Map updates.
- **Uplink**: Data Shards (ManuBase-1), ZK Proofs, Anomaly Reports.

## 3. Robot Control Loop
- **Input**: Egocentric Vision + LeRobot Policy.
- **Inference**: Running on local NPU (TensorRT).
- **Output**: Real-time motor commands via CAN/EtherCAT.
