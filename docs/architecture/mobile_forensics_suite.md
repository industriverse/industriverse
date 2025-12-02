# Mobile Surveillance Forensics Suite (MSFS) Architecture
> **"The Pocket Iron Dome."**

## 1. System Overview
The MSFS is a cross-platform (Android/iOS) system that detects surveillance not by looking for *signatures* (which change), but by measuring *physics* (which doesn't). It correlates **Energy**, **Network**, and **Permissions** to identify hostile actors.

### 1.1 The "Separate Project" Structure
To ensure this can be published globally, we structure it as a standalone module within the Industriverse monorepo, capable of being built into independent binaries/APIs.

```
src/mobile/
├── agent/              # The On-Device Logic (Python/Kotlin/Swift)
│   ├── core.py         # Telemetry Collection Loop
│   ├── energy.py       # Thermodynamic Analysis (Battery/Heat)
│   └── network.py      # Packet Timing & Metadata
├── backend/            # The Cloud/Local Collector
│   ├── collector.py    # FastAPI Ingest
│   └── analyzer.py     # Anomaly Detection Engine
├── analysis/           # The Forensics Core
│   ├── behavior_map.py # Permission-to-Energy Graph
│   └── risk_score.py   # "Surveillance Index" Calculator
└── swarm/              # A2A Integration
    └── gossip.py       # Threat Sharing Protocol
```

---

## 2. The User Value Proposition (The "Hook")
To reach a global audience, we frame security in terms of **Value**, not just Fear.

| User Archetype | Value Prop | Feature |
| :--- | :--- | :--- |
| **The Average User** | "Save Battery & Speed Up Phone" | **Thermodynamic Health**: Kill spying apps to reclaim 20% battery life. |
| **The Privacy Advocate** | "See Who Is Watching" | **Visual Aura**: 3D visualization of data leaving the phone. |
| **The Activist** | "Prove You Are Targeted" | **ZK-Evidence**: Cryptographic proof of surveillance for court/press. |
| **The Enterprise** | "Secure The Fleet" | **Fleet Radar**: Global heatmap of compromised employee devices. |

---

## 3. Technical Components

### 3.1 The Thermodynamic Agent (TTA)
*   **Role**: Runs on the device (simulated in Python for now).
*   **Input**:
    *   `BatteryCurrent` (mA)
    *   `CPULoad` (%)
    *   `NetworkBytes` (Tx/Rx)
    *   `WakeLocks` (Count/Duration)
*   **Logic**:
    *   Calculates `EnergyPerByte`. High energy + Low user interaction = **Surveillance**.
    *   Detects `PhantomWake`: Device waking up when screen is off.

### 3.2 The Network Forensics Engine
*   **Role**: Analyzes traffic metadata (no payload).
*   **Logic**:
    *   **Burst Analysis**: Surveillance sends periodic "heartbeats".
    *   **Timing Correlation**: Did `Camera` permission trigger 10ms before `Network` upload?

### 3.3 The A2A Swarm (Herd Immunity)
*   **Role**: Share threat intelligence.
*   **Protocol**:
    1.  Device A detects "App X" behaving badly.
    2.  Device A generates a **Behavior Signature** (e.g., "WakeLock every 5m + 50kb upload").
    3.  Device A broadcasts Signature to Swarm.
    4.  Device B receives Signature and blocks "App X" preemptively.

---

## 4. Data Privacy (Zero-Knowledge)
*   **Principle**: We never upload user data (SMS, Photos, etc.).
*   **Mechanism**: We upload **ZKP (Zero-Knowledge Proofs)**.
    *   *Proof*: "I certify that App X accessed the Microphone at 03:00 AM."
    *   *Secret*: The actual audio data (never leaves device).

---

## 5. Deployment Strategy
1.  **Alpha**: Python-based simulation (running on desktop, mocking mobile).
2.  **Beta**: Android APK (Kotlin) + iOS TestFlight (Swift).
3.  **Global**: Pre-installed on secure devices or downloadable via App Stores.
