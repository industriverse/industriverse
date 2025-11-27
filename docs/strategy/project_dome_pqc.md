# Project DOME: Defense-Oriented Mission Encryption (PQC)

**Mission:** Systematically integrate Post-Quantum Cryptography (PQC) across the Industriverse/NOVA platform to ensure long-term data confidentiality, integrity, and authenticity against future quantum threats, particularly for defense, national security, and critical industrial applications.

---

## Phase 1: Foundational PQC Research, EKIS Enhancement & Secure Channel PoC
**Target Duration:** 3 Sprints / 6 Weeks
**Objective:** Establish core PQC capabilities within EKIS, demonstrate hybrid PQC-secured communication, and benchmark performance.

### 1.1. PQC Algorithm & Library Finalization
*   **Algorithms:**
    *   **KEM:** CRYSTALS-Kyber (NIST Standard).
    *   **Signatures:** CRYSTALS-Dilithium (NIST Standard).
*   **Libraries:** Open Quantum Safe (liboqs) Python wrapper or equivalent production-grade library.
*   **Deliverables:**
    *   `docs/pqc_algorithm_selection.md`
    *   `tests/pqc_benchmarks/` (Benchmark scripts for KeyGen, Encap/Decap, Sign/Verify).

### 1.2. EKIS Enhancement for PQC Key Management
*   **Design:**
    *   Hybrid storage: PQC keys alongside classical keys.
    *   HSM/Vault integration for PQC private keys.
*   **Implementation:**
    *   Update `EKISService` to generate/store Kyber/Dilithium keys.
    *   New API endpoints: `/keys/pqc/generate`, `/keys/pqc/{id}/public`.
*   **Deliverables:**
    *   Updated `EKIS` service with PQC support.

### 1.3. EKIS PQC Cryptographic Operations
*   **Design:** API endpoints for crypto operations using managed keys (server-side signing/decapsulation).
*   **Implementation:**
    *   `/crypto/pqc/sign` (Dilithium)
    *   `/crypto/pqc/verify` (Dilithium)
    *   `/crypto/pqc/encapsulate` (Kyber - Client side usually, but server support needed)
    *   `/crypto/pqc/decapsulate` (Kyber - Server side private key op)

### 1.4. PQC-Secured Communication Channel PoC (Hybrid Mode)
*   **Protocol:**
    1.  **Key Establishment:** Hybrid ECDH + Kyber KEM -> Shared Session Key.
    2.  **Authentication:** Hybrid ECDSA + Dilithium Signatures.
*   **Target:** A2A Message Exchange (e.g., App Layer -> Workflow Layer).
*   **Deliverables:**
    *   `common/secure_pqc_http_client.py`
    *   Integration test demonstrating hybrid encrypted channel.

### 1.5. PQC Migration Strategy
*   **Deliverable:** `docs/project_dome/pqc_migration_strategy_v1.md`
    *   Prioritized data flows.
    *   Phased rollout plan (VIAL -> A2A -> MCP).
    *   Performance impact analysis.

---

## Phase 2: Integrating PQC into VIAL & Critical Data Paths
**Target Duration:** 4-6 Sprints / 8-12 Weeks
**Objective:** Secure the Value/Transaction Layer (VIAL) and critical MCP contexts.

### 2.1. PQC for VIAL Microservices
*   Secure internal APIs between Tokenization, Blockchain, and Payment services using the Phase 1 Hybrid Channel.

### 2.2. PQC for Blockchain Interactions
*   Investigate on-chain PQC support.
*   Secure off-chain metadata and node communication.

### 2.3. PQC for Smart Contracts
*   Sign T2L-generated contracts with Dilithium before deployment.

### 2.4. PQC for Critical MCP Contexts
*   Mandate PQC channel for sensitive contexts (e.g., "Top Secret" defense contexts).

---

## Phase 3: Platform-Wide PQC Adoption & Crypto-Agility
**Target Duration:** Ongoing
**Objective:** Broad adoption and crypto-agility.

### 3.1. Crypto-Agility Framework
*   Versioned cryptographic schemes in EKIS to allow algorithm swapping.

### 3.2. Edge PQC (BitNet)
*   Lightweight PQC for resource-constrained edge devices (Industrial Sovereign Capsules).

### 3.3. Monitoring
*   Grafana dashboards for PQC key usage and performance overhead.

---

## Success Criteria
1.  **EKIS PQC:** Functional KeyGen/Sign/Decap for Kyber/Dilithium.
2.  **Hybrid Channel:** Proven secure communication between two services.
3.  **Benchmarks:** Clear understanding of latency/CPU cost.
4.  **Strategy:** A clear path to full defense-grade security.
