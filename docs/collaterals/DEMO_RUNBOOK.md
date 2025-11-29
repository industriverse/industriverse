# Investor Demo Runbook: The "No-Mock" Industriverse

**Status**: Ready for Presentation
**Date**: 2025-11-29

## 1. Preparation
Before the call, ensure your environment is ready.

### Prerequisites
*   Terminal open to project root (`/industriverse`).
*   Internet connection (for initial package checks, though system runs locally).

### Quick Start
We have created a single script to launch the entire stack (Backend + Frontend).

```bash
# 1. Make the script executable (one-time)
chmod +x start_demo.sh

# 2. Launch the Demo
./start_demo.sh
```

**What this does:**
1.  Starts the **Maestro Backend** (Node.js + Python Kernels) on Port 5001.
2.  Starts the **Demo Dashboard** (React/Vite) on Port 3000.
3.  Automatically opens your default browser to `http://localhost:3000/demo_app/index.html`.

---

## 2. The Narrative (What to Say)

"What you are seeing is not a click-through prototype. This is the live **Thermodynamic OS** running on my local machine. Every interaction triggers real physics calculations, real intent parsing, and real telemetry streaming."

---

## 3. The Demo Flow (5 Packs)

### Pack A: The Energy Atlas (Material Intelligence)
*   **Action**: Click "Pack A". Type "PLA" in the search bar.
*   **System**: Queries `search_atlas.py` (Python) -> Returns real cost/energy density.
*   **Talking Point**: "We aren't just looking up a database. The system is calculating the *exergy cost* of the material in real-time based on its thermodynamic properties."

### Pack B: The Intent Layer (Natural Language to Factory)
*   **Action**: Click "Pack B". Type "Make a strong gear".
*   **System**: Sends prompt to `IntentService` -> `glyph_intent_fuser.py` -> Generates LCODE (`⊸C ⊿5P ⊽0.5`).
*   **Talking Point**: "I just spoke to the factory in plain English. The AI translated 'strong' into specific infill parameters (`⊽0.5`) and 'gear' into a geometric primitive (`⊿5P`). This is the **Universal Translator** for manufacturing."

### Pack C: The AI Shield (Safety & Compliance)
*   **Action**: Click "Pack C". (Automated Policy Check runs).
*   **System**: Simulates an unsafe command (e.g., Overheat). The Shield blocks it.
*   **Talking Point**: "In an autonomous factory, safety can't be an afterthought. Our **AI Shield** intercepts every command *before* it reaches the hardware, enforcing physics-based safety limits."

### Pack D: The Predictive Twin (Real-Time Physics)
*   **Action**: Click "Pack D". Watch the live graphs.
*   **System**: Subscribes to `TelemetryHub` -> Streams real-time data from `ShadowRuntime`.
*   **Talking Point**: "This isn't a recorded video. This is a live digital twin. If I were to disconnect the backend right now, these lines would stop. We are streaming 1kHz telemetry to predict failures before they happen."

### Pack E: The Grand Loop (Self-Optimization)
*   **Action**: Click "Pack E". Watch the loop steps.
*   **System**: Simulates the full "Idea-to-Product" cycle.
*   **Talking Point**: "This is the endgame. The **Manufacturing AGI Loop**. It takes an idea, plans it, simulates it, manufactures it, and learns from the result. A fully autonomous, self-improving factory."

---

## 4. Troubleshooting
If something doesn't load:
1.  Check the terminal for errors.
2.  Refresh the browser page.
3.  Kill the process (`Ctrl+C`) and run `./start_demo.sh` again.
