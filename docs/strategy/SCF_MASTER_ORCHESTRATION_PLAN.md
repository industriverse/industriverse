# SCF Master Orchestration Plan: From Genesis to Sovereignty

**Status**: Draft
**Owner**: Industriverse
**Target**: Production Readiness & Autonomous Operation

## 1. Executive Summary
The **Sovereign Code Foundry (SCF)** is now a living organ within the Industriverse. It possesses the biological structure to Observe (Pulse), Orient (Intent), Decide (GenN), and Act (Deploy). This document outlines the strategy to take the reigns of this system, transitioning from **Structural Implementation** to **Operational Sovereignty**.

## 2. The Control Plane (Handling the Reigns)
You are the **DaemonController**. You steer the organism using the **Orchestration Level Manager**.

### 2.1. The Gearbox
The system operates in four distinct modes ("Gears"):
*   **STANDARD (Level 1)**: Human-in-the-loop. Slow heartbeat (5s). High safety checks. Use for debugging and initial training.
*   **ACCELERATED (Level 2)**: Parallel hypothesis generation. Faster heartbeat (1s). Use for bulk code generation and optimization tasks.
*   **HYPER (Level 3)**: Automated Text-to-LoRA (T2L) and high mutation rates. Heartbeat (0.1s). Use for rapid prototyping and stress testing.
*   **SINGULARITY (Level 4)**: Unbounded self-improvement. Safety rails disengaged. **CAUTION**: Only for isolated, sandboxed environments.

### 2.2. Command Interface
Control the SCF via the **Control Plane** at `data/scf/control.json`.
**Example Command:**
```json
{
  "command": "SHIFT_GEAR",
  "payload": { "level": "ACCELERATED" }
}
```

## 3. Phase 1: Training (The Education of GenN)
Currently, `GenN` (Generator Network) uses mock logic. We must teach it to write real code.

### 3.1. Data Collection Strategy
1.  **Passive Observation**: Run the SCF in `STANDARD` mode connected to the `bridge_api`.
2.  **Harvesting**: The `CFRLogger` will record every Context -> Intent -> Code -> Review tuple.
3.  **Dataset Construction**:
    *   **Input**: Context Slab + Intent Spec.
    *   **Output**: Validated Code (Verdict: APPROVE).
    *   **Negative Samples**: Rejected Code (Verdict: REJECT).

### 3.2. Training Pipeline
1.  **Bootstrap**: Fine-tune a base model (e.g., Phi-4 or StarCoder) on the harvested dataset.
2.  **Reinforcement Learning (RLHF)**: Use the `EBDM` (Energy-Based Diffusion Model) scores as the reward signal to align the model with physical reality.

## 4. Phase 2: Distillation (Edge Sovereignty)
To run on edge nodes (BitNet), we must compress the intelligence.

### 4.1. The Teacher-Student Loop
*   **Teacher**: The full-scale GenN (cloud/server).
*   **Student**: A 1.58-bit quantized model (BitNet).
*   **Process**: The Teacher generates high-quality synthetic data (Reasoning Traces) to train the Student.

### 4.2. Deployment
*   Use `src/scf/canopy/deploy/bitnet_autodeploy.py` to push the distilled weights to edge nodes.

## 5. Phase 3: Live Operations (The Pulse)
Running the loop against the real world.

### 5.1. Safety Monitors
*   **Contextual Regulator**: Ensures intents match the current safety context (e.g., "Don't optimize grid during a blackout").
*   **Ethics Limiter**: Prevents generation of malicious or deceptive code.

### 5.2. Intervention Protocol
If the system diverges:
1.  **Emergency Stop**: Send `{"command": "STOP"}` to `control.json`.
2.  **Rollback**: The `DeploymentStrategy` maintains a history of deployed artifacts for instant rollback.

## 6. Next Steps (Action Plan)

### Immediate Actions (Week 1)
- [ ] **Data Harvest Run**: Run the Daemon in `STANDARD` mode for 24 hours to collect initial telemetry and mock generation logs.
- [ ] **Pipeline Setup**: Configure the `GenN` training script to consume `CFR` logs.

### Mid-Term Actions (Month 1)
- [ ] **Model Swap**: Replace `GenN` mock with the first fine-tuned model checkpoint.
- [ ] **Energy Atlas Calibration**: Update `EnergyAtlas` with real sensor data from the field.

### Long-Term Vision (Quarter 1)
- [ ] **Full Autonomy**: Enable `HYPER` mode for autonomous grid optimization.
- [ ] **Self-Replication**: Allow the SCF to propose improvements to its own `TrifectaMasterLoop`.
