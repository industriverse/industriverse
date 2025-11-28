# Industriverse Public Launch Strategy
**Status**: DRAFT

## 1. The "Safe Version" (Public Release)
The public version of Industriverse is designed to demonstrate capability without revealing the core IP.

### Included Components (Safe)
*   **The CLI (`dac-builder`)**: A fully functional CLI for defining tasks and managing capsules.
*   **The Capsule Protocol**: The full specification of `capsule://` to encourage adoption as a standard.
*   **Mock Services**:
    *   `MockTNN`: Returns random or heuristic-based energy values.
    *   `MockEBDM`: Returns pre-canned designs or simple noise-based generations.
*   **Visualization Tools**: The `DiffusionExplorer` (frontend only) to visualize pre-computed paths.

### Excluded Components (Private)
*   **Real Physics Priors**: The actual equations in `src/ebm_lib/priors`.
*   **TNN Weights**: The trained weights of the thermodynamic predictors.
*   **Discovery Loop Logic**: The meta-learning orchestration code.

## 2. The Launch Narrative
*   **Headline**: "The First Thermodynamic AI Platform for Industrial Discovery."
*   **Value Prop**: "Stop Hallucinating. Start Engineering. Industriverse guarantees physical validity in Generative AI."
*   **Call to Action**: "Download the CLI to mint your first Capsule. Request access to the Engine for real physics optimization."

## 3. Investor Portal (Private)
A secure, password-protected web portal for investors and partners.
*   **Content**:
    *   The "Grand Unified Demo" video.
    *   Interactive "Real Physics" dashboard (connected to the Private Engine).
    *   The "Internal IP Summary" (under NDA).

## 4. Timeline
*   **Week 1**: Internal IP Audit & Vault Timestamping (Complete).
*   **Week 2**: Provisional Patent Filing.
*   **Week 4**: "Safe Version" Code Cleanup & Public Repo Creation.
*   **Week 6**: Public Launch & Press Release.
