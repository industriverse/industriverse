# Manufacturing AGI Loop: User Manual

## Overview
The **Manufacturing AGI Loop** is a self-correcting, physics-aware industrial intelligence system. It translates natural language intent into optimal machine actions, protected by thermodynamic safety gates.

## Core Components
1.  **Maestro Conductor**: The central brain.
2.  **Intent Kernel**: Translates "Lightweight" -> `⊽0.1`.
3.  **Capsule Network**: Distributed machine intelligence.
4.  **AI Shield v3**: Thermodynamic cybersecurity.
5.  **Simulation Oracle**: Physics-based prediction.
6.  **Shadow Twin**: Real-time deviation detection.

## Quick Start

### 1. Start the System
```bash
python3 src/loop/agi_controller.py
```

### 2. Submit an Intent
The system accepts natural language prompts.
*   *"Make a strong gear."*
*   *"Make a precision housing."*

### 3. Monitor Execution
The console will show the full thought process:
*   [Intent] -> [Dispatch] -> [Planning] -> [Safety] -> [Oracle] -> [Execution]

## Safety Protocols
*   **E-STOP**: Triggered automatically if Thermal Drift > 10°C.
*   **Sanitization**: RPMs > 12,000 are automatically clamped.
*   **Rejection**: Plans with forbidden glyph sequences are rejected.

## Troubleshooting
*   **"No capable capsules found"**: Check `src/capsules/definitions`.
*   **"Unsafe Plan"**: Check `src/safety/glyph_safety.py` rules.
*   **"Anomaly Detected"**: Check machine telemetry or simulation tolerance.
