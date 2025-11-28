# Industriverse Operational Timetable: The Regiment of Value

**Objective:** Systematize the execution of the "Value Loop" to guarantee consistent, physics-verified delivery.
**Role:** Commander (Human) vs. Lieutenant (Agent/Script).

---

## The Daily Cycle (24-Hour Loop)

### 🌅 08:00 - The Morning Brief (Review)
**Goal:** Assess overnight optimization results and system health.
*   **Action (Human)**: Open `docs/reports/master_value_report.md` (or latest daily report).
*   **Checklist**:
    *   [ ] Did `orchestrate_full_regiment.py` run successfully overnight?
    *   [ ] **Is the IDF API Server running?** (Required for Frontend)
        ```bash
        python frameworks/idf/api/server.py > logs/idf_api.log 2>&1 &
        ```
    *   [ ] Are there any **Safety Violations** in the AI Shield logs?
    *   [ ] What is the **Total Energy Saved** ($\Delta E$) across all active contracts?
*   **Tool**: `cat artifacts/strike_runs/*_full.json | grep "energy_delta"`

### 🎯 09:00 - The Strike (Execution)
**Goal:** Execute high-value, manual interventions for specific clients.
*   **Action (Human)**: Identify the "Target of the Day" (e.g., a new client constraint).
*   **Command**:
    ```bash
    # Example: Optimize Fusion Plasma for Client X
    python scripts/value_loop/run_client_strike_loop.py --domain fusion
    ```
*   **Outcome**: A verified JSON proof and deployment ID within 5 minutes.

### 🤖 12:00 - The Autopilot Check (Monitoring)
**Goal:** Ensure the autonomous daemon is healthy.
*   **Action (Agent/Daemon)**: `orchestrate_full_regiment.py` continues running in background.
*   **Action (Human)**: Verify process status.
    ```bash
    ps aux | grep orchestrate_full_regiment
    tail -n 20 logs/orchestrator.log
    ```

### 🛡️ 14:00 - The Shield Audit (Safety)
**Goal:** Deep dive into thermodynamic compliance.
*   **Action (Human)**: Run a manual safety verification on a complex configuration.
*   **Command**:
    ```bash
    python scripts/value_loop/verify_safety_compliance.py --config_json artifacts/strike_runs/latest_opt.json
    ```
*   **Why**: To ensure the "AI Lieutenant" isn't drifting into unsafe entropy zones.

### 🚀 16:00 - The Deployment (Expansion)
**Goal:** Push new capabilities to the Sovereign Gateway.
*   **Action (Human)**: Deploy a newly scaffolded capsule.
*   **Command**:
    ```bash
    python scripts/value_loop/deploy_sovereign_dac.py --manifest src/capsules/sovereign/new_domain_v1/manifest.yaml
    ```

### 🌙 18:00 - The Synthesis (Reporting)
**Goal:** Finalize the day's value for client billing/updates.
*   **Action (Agent)**: `generate_value_report.py` aggregates all runs.
*   **Action (Human)**: Send the "Daily Value Summary" to stakeholders.

---

## The Weekly Cycle (Evolution)

### Monday: Strategy Alignment
*   **Focus**: Review `docs/strategy/10_immediate_value_opportunities.md`.
*   **Task**: Pick 1-2 new domains to "Harden" (create `_v1.py` priors).

### Wednesday: TNN Simulation Deep Dive
*   **Focus**: Run long-horizon simulations to test stability.
*   **Command**:
    ```bash
    python scripts/value_loop/simulate_tnn_dynamics.py --capsule grid --steps 1000 --use_diffusion
    ```

### Friday: System Upgrade (Phase Shift)
*   **Focus**: Update the IDF Engine or AI Shield logic.
*   **Task**: Refactor `frameworks/idf/core/` based on weekly learnings.

---

## Automation Roadmap (Human -> Agent)

| Task | Current Owner | Future Owner (Agent) | Trigger |
| :--- | :--- | :--- | :--- |
| **Morning Brief** | Human | **Reporting Agent** | Daily Cron |
| **The Strike** | Human | **Sales Agent** | Email Ingestion |
| **Shield Audit** | Human | **Safety Sentinel** | Anomaly Detection |
| **Deployment** | Human | **DevOps Agent** | Git Merge |
| **Code Hardening**| Human | **Research Agent** | Weekly Loop |

**Your Goal**: Move every item from "Current Owner" to "Future Owner" by refining the scripts in `scripts/value_loop/`.
