# Empeiria Haus: Orchestration SOP & Training Manual

**Version**: 1.0
**Status**: Production Ready
**Classification**: INTERNAL USE ONLY

---

## 1. Overview
This Standard Operating Procedure (SOP) defines the protocols for operating the **Empeiria Haus Industrial Intelligence Platform**. It serves as a checklist for the "Operator" (you) to demonstrate, deploy, and market the system with machine-like precision.

---

## 2. System Initialization Protocol
**Objective**: Ensure the Quadrality Engine is primed for execution.

- [ ] **Verify Environment**: Ensure Python 3.9+ and dependencies are installed.
- [ ] **Check Data**: Confirm `scripts/demos/demo_scenarios.json` and `src/marketing/solution_matrix.json` are present.
- [ ] **Verify Mocks**: Ensure `EnergyAPI` and `VisualTwin` have access to their local data/mocks.

---

## 3. The Giant Demo (The Showstopper)
**Objective**: Execute the "Entropy to Equity" narrative for high-stakes investor meetings.

**Narrative Arc**:
1.  **Thermodynamics**: Kairos validates energy price.
2.  **Negotiation**: A2A wins the contract.
3.  **Physics**: Aletheia detects drift -> Telos heals -> DriftCanceller corrects.
4.  **Economics**: Ledger mints Negentropy Credits.

**Execution Checklist**:
- [ ] **Command**: `python3 scripts/demos/giant_demo_orchestration.py`
- [ ] **Verification**: Watch for the `[DriftCanceller] ✅ Resumed with Precision` log line.
- [ ] **Talking Point**: "You just watched a factory think, heal, and profit autonomously."

---

## 4. The Demo Factory (Client Specifics)
**Objective**: Demonstrate specific capabilities tailored to a client's industry.

**Protocol**:
1.  **Identify Client Industry**: (e.g., Manufacturing, Energy, Robotics).
2.  **Select Scenario ID**: Refer to `scripts/demos/demo_scenarios.json`.
    *   **ID 1**: Zero-Drift CNC (Manufacturing)
    *   **ID 11**: Smart Grid Load Balancing (Energy)
    *   **ID 31**: Capsule Negotiation (Supply Chain)
    *   **ID 41**: Dark Factory (Advanced)
3.  **Execute**:
    - [ ] **Command**: `python3 scripts/demos/demo_factory.py --id <ID>`
4.  **Verification**: Confirm the specific module (e.g., `RoboCOIN`) activates in the logs.

---

## 5. The Solution Architect (Sales Engineering)
**Objective**: Map a client's vague natural language problem to a precise technical solution.

**Protocol**:
1.  **Input**: Receive client query (e.g., "How do I stop my welding robots from drifting?").
2.  **Execute**:
    - [ ] **Command**: (Interactive Mode)
      ```python
      from src.marketing.solution_architect import SolutionArchitect
      arch = SolutionArchitect()
      print(arch.map_request_to_solution("stop welding robots from drifting"))
      ```
3.  **Output Analysis**:
    *   **Pitch**: Use the returned "Pitch" string in your email/proposal.
    *   **Modules**: List the returned modules (e.g., `DriftCanceller`, `VisualTwin`) as the "Bill of Materials".

---

## 6. The Social Launch Engine (Outreach)
**Objective**: Deploy a coordinated 4-Day Social Media Campaign across 3 personas.

**Protocol**:
1.  **Generate Content**:
    - [ ] **Command**: `python3 scripts/marketing/social_launch_engine.py`
2.  **Review Output**: Open `docs/marketing/social_calendar_4day.md`.
3.  **Deploy**:
    *   **Day 1**: Post "We Are Here" content.
    *   **Day 2**: Post "Proof of Work" (Giant Demo logs).
    *   **Day 3**: Post "Client Solutions" (Architect examples).
    *   **Day 4**: Post "The Movement" (TOS-1 Standard).

---

## 7. Troubleshooting & Hardening
**Objective**: Handle system drift or demo failures.

- [ ] **Drift Detected**: If `VisualTwin` fails to ingest, check `data/egocentric_index.json`.
- [ ] **Negotiation Failure**: If `NegotiationEngine` rejects bids, check `max_price` in the scenario config.
- [ ] **Logging**: If logs are silent, ensure `logging.basicConfig(level=logging.INFO)` is set in the module.

---

**"We do not guess. We measure. We correct. We execute."**
