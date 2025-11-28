# Trifecta Standard Operating Procedure (SOP)

**Version:** 1.0
**Date:** 2025-11-27
**System:** Industriverse Trifecta Orchestration

## 1. Overview
The Trifecta Orchestration Loop is the "Conscious" operating mode of the Industriverse. It unifies **ACE** (Context), **UserLM** (Intent), **RND1** (Build), and **BitNet** (Deploy) to autonomously execute high-level operational goals.

## 2. Roles & Personas
Select the appropriate persona for your goal to guide UserLM's behavior:

| Persona | Role | Best For |
| :--- | :--- | :--- |
| **Operator** | Grid/Plant Manager | Efficiency, Load Balancing, Safety |
| **Physicist** | R&D Scientist | Fusion Stability, Material Science, Simulation |
| **Logistics Manager** | Supply Chain Lead | Latency, Throughput, Inventory |
| **Auditor** | Compliance Officer | Regulation, Safety Checks, Verification |
| **VC** | Investor/Executive | ROI, KPI Visualization, High-level Strategy |

## 3. Execution Procedures

### 3.1. Via CLI (Headless Mode)
Use for automated testing or backend verification.
```bash
python scripts/run_trifecta_loop.py --goal "Your Goal Here" --persona "Your Persona"
```

### 3.2. Via Portal (Intuitive Mode)
Use for standard operations and visual monitoring.
1.  **Access**: Navigate to the Main Portal.
2.  **Activate**: Click the "Trifecta Console" button (or use Voice Command "Open Console").
3.  **Input**:
    *   **Text**: Type your goal in the command line.
    *   **Voice**: Click the microphone and speak your goal (e.g., "Optimize Fusion for Stability").
4.  **Monitor**: Watch the live "Conscious Loop" logs as the system reflects, plans, builds, and deploys.
5.  **Result**: Review the final score and deployment status.

## 4. Interpreting Results

### 4.1. Log Stages
*   **[ACE]**: The system is recalling past strategies. *Check: Is the Playbook relevant?*
*   **[UserLM]**: The system is validating the plan against the persona. *Check: Did it approve?*
*   **[RND1]**: The system is simulating the physics. *Check: Is the Score > 0.4?*
*   **[BitNet]**: The system is deploying code. *Check: Are nodes active?*

### 4.2. Troubleshooting
*   **UserLM Rejection**: The goal may be unsafe or unclear. Refine the prompt.
*   **Simulation Failure**: The physical parameters may be impossible. RND1 will attempt to self-correct in future versions.
*   **Deployment Error**: Check edge node connectivity.

## 5. Safety Protocols
*   **AI Shield** is active during the UserLM phase. Any malicious or unsafe intent will be rejected immediately.
*   **Human-in-the-Loop**: The Operator can abort the loop at any time by closing the console or issuing a "Stop" voice command.
