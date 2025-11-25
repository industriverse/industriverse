# Industriverse Portal UX Mockups

## Overview
The **Industriverse Portal** provides a unified "Single Pane of Glass" for monitoring and interacting with the 27 Sovereign Capsules.

## 1. Dashboard View: "The Constellation"
**Visual Style:** Dark mode, high-contrast neon accents (Cyberpunk/Sci-Fi aesthetic).

### Layout
- **Header:** "THERMODYNAMIC DISCOVERY LOOP V16 - SYSTEM STATUS: ONLINE" (Green Pulse)
- **Main Grid:** 27 Cards arranged in a 7x4 grid (with spacers).
- **Sidebar:** Global Metrics (Total Energy, Total Proofs, Active Alerts).

### Capsule Card Design
Each card represents one Sovereign Capsule.
- **Color Coding:**
    - **Category A (High Energy):** Glowing Red/Orange Border
    - **Category B (Flow/Heat):** Deep Blue/Cyan Border
    - **Category C (Swarm):** Neon Green Border
    - **Category D (Multi-physics):** Purple/Violet Border

- **Content:**
    - **Title:** e.g., "Fusion Control" (Bold, White)
    - **Status:** "ACTIVE" (Green Dot) or "IDLE" (Grey Dot)
    - **Sparkline:** Real-time Energy Usage (J/s)
    - **PRIN Score:** Badge (e.g., "0.95") - Color graded (Green > 0.75, Yellow > 0.60, Red < 0.60)
    - **UTID:** Last 6 chars of latest UTID (e.g., `#A1B2C3`)

## 2. Capsule Detail View
Clicking a card opens the Detail View overlay.

### Sections
1.  **Thermodynamic Topology:** 3D visualization of the Energy Map (Heatmap style).
2.  **Live Stream:** Log of recent ACE reasoning steps ("Thinking...").
3.  **Proof Lineage:** DAG visualization showing parent/child proofs.
4.  **Controls:**
    - "Trigger Discovery Loop" (Button)
    - "Adjust Safety Budget" (Slider)
    - "View Source Equations" (Link)

## 3. Deployment Manager
For Operators (Kube Operator View).
- **List View:** Table of all 27 Deployments.
- **Columns:** Name, Replicas, CPU/Mem Usage, Energy Budget, Status.
- **Actions:** Scale Up/Down, Rollback, View Logs.
