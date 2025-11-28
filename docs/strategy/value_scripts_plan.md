# Implementation Plan: The 7 Value Scripts

## Goal
Develop a cohesive suite of 7 scripts that operationalize the **Industriverse Value Loop**, enabling engineers to go from "Client Constraint" to "Verified Proof & Deployment" in a single workflow.

## The 7 Scripts

### 1. `run_client_strike_loop.py` (End-to-End)
- **Purpose**: The "Master Key" for the engineer. Takes a domain and constraints, runs the full loop.
- **Workflow**: Input -> Map -> IDF Solve -> Shield Verify -> Deploy -> Report.
- **Inputs**: `--domain`, `--constraint_json`
- **Outputs**: JSON Proof, Deployed Activity ID.

### 2. `deploy_sovereign_dac.py` (Deployment)
- **Purpose**: Deploys a Sovereign Capsule to the Gateway.
- **Action**: Reads `manifest.yaml`, registers with `CapsuleGatewayService`, initializes `ThermodynamicRuntimeMonitor`.
- **Gap Fill**: Connects static files to runtime service.

### 3. `optimize_diffusion_service.py` (IDF API)
- **Purpose**: CLI for the Energy-Based Diffusion Engine.
- **Action**: Calls `frameworks/idf/api/server.py` (or local lib) to optimize a configuration.
- **Gap Fill**: Exposes IDF to the command line.

### 4. `verify_safety_compliance.py` (AI Shield)
- **Purpose**: Pre-deployment safety check.
- **Action**: Runs `ThermodynamicAIConstraints` against a proposed state vector.
- **Gap Fill**: Wires "Simulation" safety logic to actual deployment pipeline.

### 5. `simulate_tnn_dynamics.py` (TNN+IDF)
- **Purpose**: Runs time-domain simulations using Diffusion Dynamics.
- **Action**: Wraps TNN `simulate` but injects stochastic noise from IDF.
- **Gap Fill**: Unifies TNN ODEs with Langevin Diffusion.

### 6. `generate_value_report.py` (Reporting)
- **Purpose**: Client-facing documentation.
- **Action**: Reads run artifacts, calculates "Energy Saved" and "Stability Score", generates Markdown/PDF.
- **Gap Fill**: Automates the "Deliver" phase.

### 7. `orchestrate_full_regiment.py` (Master Loop)
- **Purpose**: Continuous Integration / Continuous Value.
- **Action**: Runs the Strike Loop for *all* active client contracts (simulated).
- **Gap Fill**: Scales the manual process to a background daemon.

## Execution Order
1. `optimize_diffusion_service.py` (Core Engine)
2. `verify_safety_compliance.py` (Safety Gate)
3. `deploy_sovereign_dac.py` (Deployment)
4. `simulate_tnn_dynamics.py` (Simulation)
5. `generate_value_report.py` (Reporting)
6. `run_client_strike_loop.py` (Integration)
7. `orchestrate_full_regiment.py` (Scaling)
