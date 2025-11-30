# Service Mesh Architecture: The Sleeping Army

**Technical Specification for B2 Integration and Capsule Resolution.**

---

## 1. The Concept
We have 700+ services (The "Sleeping Army") stored as **Capsules** in Backblaze B2. Keeping them all running is thermodynamically inefficient (high entropy/cost).
**Solution**: Store them frozen. Hydrate them Just-in-Time (JIT).

## 2. The Capsule URI Scheme
We introduce a new URI scheme for the Orchestrator:
`capsule://<dac_id>/<service_name>:<version>`

Example: `capsule://industriverse-dac/welding-sim:v2.1`

## 3. Component Architecture

### A. The Capsule Resolver (`src/orchestration/capsule_resolver.py`)
*   **Input**: `capsule://...`
*   **Function**:
    1.  Queries the **DAC Registry** (Mocked for now) to find the B2 location.
    2.  Verifies the **ZK Proof** (Signature) to ensure the code hasn't been tampered with.
    3.  Returns: `b2://my-bucket/capsules/welding-sim-v2.1.tar.gz`

### B. The Hydrator (`src/orchestration/hydrator.py`)
*   **Input**: `b2://...`
*   **Function**:
    1.  Checks Local Cache (NVMe). If present, return path.
    2.  If missing, downloads from Backblaze B2.
    3.  Unpacks to `runtime/services/<service_name>`.
    4.  Updates `TaskDB` with "Hydration Cost" (Bandwidth + Time).

### C. Kairos Integration (Pre-Warming)
*   **Logic**:
    *   Standard: "Hydrate when requested." (High Latency).
    *   **Pre-Warming**: "It is 2 AM. Energy is $0.05/kWh. The 'Morning Shift' usually requests 'Welding Sim'. **HYDRATE NOW**."

## 4. Security (The Airlock)
*   **Rule**: No code runs without a valid ZK Proof.
*   **Enforcer**: `Telos` checks the Resolver's verification result before allowing `Executor` to start the container.

## 5. Data Flow
1.  **Task Submitted**: `source: capsule://...`
2.  **Chronos**: Sees `capsule://`. Calls `Hydrator`.
3.  **Hydrator**: Calls `Resolver` -> `B2` -> Download.
4.  **Kairos**: Records cost.
5.  **Executor**: Runs the hydrated service.
