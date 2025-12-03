# Executive Runbook: The Owner's Manual

**"How to Run the Thermodynamic Monopoly"**

This document contains the Standard Operating Procedures (SOPs) for operating Empeiria Haus.

---

## 1. Client Onboarding
**Goal**: Set up a secure, optimized workspace for a new client.

1.  **Receive Brief**: Send `templates/client_brief.json` to the client.
2.  **Ingest**: Run the intake script.
    ```bash
    python3 scripts/client/ingest_request.py client_brief.json
    ```
3.  **Verify**: Check `projects/{client_name}/project_config.json`.

---

## 2. Running the Factory (Orchestration)
**Goal**: Solve the client's problem using the Trifecta Brain.

1.  **Select Persona**: Choose the right persona for the job.
    *   `research_lead`: For maximum innovation (High Risk/Reward).
    *   `safety_officer`: For critical infrastructure (Zero Risk).
    *   `financial_auditor`: For cost reduction.
2.  **Launch**:
    ```bash
    python3 scripts/trifecta/run_orchestration.py --persona research_lead
    ```
3.  **Monitor**: Watch the `EmpeiriaDashboard` for "Research Events".

---

## 3. Delivering Value
**Goal**: Generate the "Proof of Value" artifacts.

1.  **Generate Audit (TGE)**:
    ```bash
    python3 scripts/research/generate_tge_audit.py --client {client_name}
    ```
2.  **Generate Certificate (ZKMM)**:
    ```bash
    python3 scripts/research/generate_zk_proof.py --part {part_id}
    ```
3.  **Deliver**: Send the files from `examples/client_deliverables/` to the client.

---

## 4. System Maintenance
**Goal**: Ensure the machine stays clean.

1.  **Check Heartbeat**: `curl http://localhost:8000/status`
2.  **Prune Vault**: Archive old secrets to Cold Storage (B2) every 30 days.

> "Trust the Process. Trust the Physics."
