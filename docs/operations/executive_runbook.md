# Empeiria Haus | Executive Runbook

**"The Owner's Manual for the Thermodynamic Monopoly."**

This document outlines the Standard Operating Procedures (SOPs) for running Empeiria Haus as a client-facing research institute.

---

## 1. Client Onboarding (The Handshake)
When a new prospect approaches Empeiria Haus:

1.  **Send the Brief**: Provide them with `templates/client_brief.json`.
2.  **Receive the Request**: Save their filled JSON to `incoming_requests/`.
3.  **Ingest the Project**:
    ```bash
    python3 scripts/client/ingest_request.py incoming_requests/acme_brief.json
    ```
    *Result*: A new secure workspace is created in `projects/Acme_Corp/`.

---

## 2. Factory Orchestration (The Operation)
Once the project is set up, you must "Run the Factory" to solve their problem.

1.  **Start the Daemon**:
    ```bash
    python3 scripts/datahub/datahub_ctl.py start
    python3 scripts/datahub/datahub_ctl.py research on
    ```
2.  **Activate the Persona**:
    Based on the client's brief (e.g., "Reduce Energy"), choose the correct persona.
    ```bash
    python3 scripts/trifecta/run_orchestration.py --persona financial_auditor
    ```
    *Result*: The system will autonomously optimize for the client's goals 24/7.

---

## 3. Value Delivery (The Artifacts)
After the factory has run for the agreed duration (e.g., 48 hours):

1.  **Generate the Proof**:
    Run the specific generator for their use case.
    *   *Energy Savings*: `python3 scripts/research/generate_tge_audit.py`
    *   *IP Protection*: `python3 scripts/research/generate_zk_proof.py`
    *   *Risk Alert*: `python3 scripts/research/generate_risk_forecast.py`

2.  **Deliver**:
    Send the generated files from `examples/client_deliverables/` to the client.

---

## 4. System Maintenance (The Manifest)
To ensure stability, always check the **System Manifest** before a major client run.
*   **File**: `config/system_manifest.json`
*   **Action**: Ensure all component versions match the manifest.

---
*© 2025 Empeiria Haus. Executive Operations.*
