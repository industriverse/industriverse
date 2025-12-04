# Sovereign Daemon & Real-World Training Implementation Plan

**Status**: FINALIZED (Amalgamated from Batch 1 & 2)
**Objective**: Transition to a production-grade, self-improving engine using a Hybrid Local/Cloud architecture.

## 1. Infrastructure Architecture

### A. The Hybrid Model
*   **Local Node (The Overseer)**:
    *   **Hardware**: User's Mac + 3TB External Drive (`/Volumes/Expansion`).
    *   **Role**: Orchestration, Fossil Storage, Model Archiving, ZK Signing, Dashboarding.
    *   **Software**: `scf_daemon.py` (Sovereign Daemon).
*   **Cloud Node (The Muscle)**:
    *   **Hardware**: RunPod GPU (NVIDIA H100 SXM 80GB).
    *   **Role**: Heavy Training (EBDM, GenN), Distillation.
    *   **Software**: Dockerized `gpu_worker.py`.

### B. Storage Partitioning (3TB Drive)
Mount Point: `/Volumes/Expansion/industriverse`
*   `fossil_vault/` (1.5 TB): Raw fossils and sharded batches (`.ndjson`, `.pkl`).
*   `energy_atlas/` (600 GB): Entropy maps, Hilbert state logs.
*   `model_zoo/` (300 GB): Checkpoints (`ebdm_genN/`, `bitnet_distilled/`).
*   `release_history/` (200 GB): Weekly immutable archives.
*   `zk_proofs/` (200 GB): Audit logs and cryptographic signatures.
*   `system_cache/` (200 GB): Temporary build artifacts.

## 2. Core Components Implementation

### A. The Sovereign Daemon (`src/scf/daemon/scf_daemon.py`)
*   **Responsibility**: The "Always-On" Orchestrator.
*   **Loop**:
    1.  **Pulse**: Check for new fossils in `fossil_vault`.
    2.  **Orient**: Create training intent.
    3.  **Decide**: Dispatch job to RunPod (or local fallback).
    4.  **Act**: Verify returned checkpoint, mint ZK proof, promote to `model_zoo`.
*   **Gears**: STANDARD (5s), ACCELERATED (1s), HYPER (0.1s), SINGULARITY (0.05s).
*   **Control**: Controlled via `data/scf/control.json` (e.g., `SHIFT_GEAR`, `STOP`).

### B. Fossil Batching Engine (`src/scf/fertilization/fossil_batcher.py`)
*   **Logic**: Stream-based processing to handle TB-scale data without RAM explosion.
*   **Format**: Newline Delimited JSON (`.ndjson`) sharded files.
*   **Features**:
    *   `stream_minibatches()`: Yields ready-to-train tensors.
    *   `iterate_fossils()`: Shuffles and streams from disk.

### C. GPU Worker (`src/scf/daemon/gpu_worker.py`)
*   **Role**: The execution unit running inside the RunPod container.
*   **Action**: Receives a job (Fossil Path + Config), runs `train_ebdm.py`, uploads checkpoint to `model_zoo`.

### D. EBDM Training Stack (`src/scf/training/train_ebdm.py`)
*   **Architecture**:
    *   **Encoder**: Physics-informed embeddings.
    *   **Score Network**: Residual MLP/U-Net predicting energy gradients.
    *   **Sampling**: Langevin Dynamics for contrastive divergence training.
*   **Loss**: Denoising Score Matching + Physics Constraints.

### E. Weekly Release Automation
*   **Script**: `scripts/release/weekly_promote.py`
    *   Selects best checkpoint from `model_zoo`.
    *   Packages into `release_history/week-YYYY-MM-DD`.
    *   Mints ZK Proof (`zk_proofs/`).
*   **CI/CD**: GitHub Actions workflow to trigger promotion and publish release notes.

## 3. Execution Roadmap

### Phase 1: Bootstrap (Immediate)
1.  **Scaffold**: Create the directory structure on `/Volumes/Expansion`.
2.  **Deploy Code**: Implement the 5 core Python files (`daemon`, `worker`, `batcher`, `trainer`, `release`).
3.  **Dockerize**: Create `docker/runpod/Dockerfile` for the cloud worker.

### Phase 2: Ingestion & Local Test
1.  **Ingest**: Run `PrimordialSoupIngestor` to populate `fossil_vault` with initial data.
2.  **Dry Run**: Run `scf_daemon.py` locally with `gpu_worker.py` in "Local Mode" to verify the loop.

### Phase 3: Cloud Link
1.  **Rent H100**: Start RunPod instance.
2.  **Sync**: Use `rsync` to push code and `fossil_vault` subset to RunPod.
3.  **Train**: Dispatch first real EBDM training job.

### Phase 4: Autonomy
1.  **Daemonize**: Set up `systemd` or `cron` to keep `scf_daemon.py` running.
2.  **Release**: Schedule the first "Weekly Drop".

## 4. "Secret Sauce" Tools
*   **Fossil Validator**: Enforce provenance (CID + Verifier Result).
*   **Negentropy Ledger**: Mint credits for energy savings.
*   **Emergency Stop**: Hardware/Software lock file (`data/scf/EMERGENCY_LOCK`).
