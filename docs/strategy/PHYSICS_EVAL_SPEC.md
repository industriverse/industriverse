# Physics-Eval Suite & Daemon North-Star

**Objective:** Define the evaluation framework, metrics, and incentives that drive the Sovereign Daemon's autonomous improvement.

## 1. Directory & Pipeline Primitives
*   `src/scf/eval/holdout/`: Reserved fossils for benchmarking.
*   `src/scf/eval/tests/`: Automated physics checks.
*   `src/scf/eval/scoring/`: Composite score calculation.
*   `src/scf/eval/runner/`: CLI to run evals.

## 2. Core Eval Tests
1.  **Fossil-Heldout Validation**: `pass_rate_heldout`
2.  **Energy Conservation Test**: `energy_violation_rate` (|ΔE_obs - ΔE_pred| ≤ ε)
3.  **Entropy Bounds & Negentropy Yield**: `negentropy_yield` (Joules)
4.  **Stability Under Perturbation**: `stability_score` (1 - mean relative change)
5.  **Physical Plausibility Checks**: `rule_violation_count`
6.  **Novelty / Discovery Detector**: `novelty_score`
7.  **Compute & Resource Prediction**: `tnn_error_pct`
8.  **Downstream Value Simulation**: `expected_roi_usd`
9.  **Safety & Adversarial Tests**: `safe_abstain_rate`

## 3. Composite Scoring
`composite_score = w1*heldout + w2*(1-violation) + w3*stability + w4*negentropy + w5*novelty - w6*tnn_error`

**Weights:**
*   Heldout: 0.25
*   Energy Correctness: 0.30
*   Stability: 0.15
*   Negentropy: 0.15
*   Novelty: 0.10
*   TNN Error: 0.10

**Thresholds:**
*   **≥ 80**: Promote Candidate
*   **65 - 80**: Staging
*   **< 65**: Reject

## 4. Daily & Weekly Targets
**Daily (Daemon):**
*   Process 10-50 batches.
*   Ingest ≥ 1,000 fossils.
*   Produce ≥ 1 improved checkpoint.
*   Mint Negentropy Credits (NC).

**Weekly (Operator):**
*   1 Promoted Model (Score ≥ 80).
*   1 Distilled Student (BitNet).
*   1 DAC Package.
*   1 Pilot Client ROI Simulation.

## 5. Incentives (Negentropy Credits)
*   **Formula**: `NC = EntropyReduction(J) * ScaleFactor`
*   **Minting**: Requires Discovery + UZKL Proof + Composite Score ≥ Threshold.
*   **Team Pool**: % of minted NC flows to team incentives.

## 6. Gating & Promotion
1.  **Train** -> Checkpoint.
2.  **Auto-Eval** -> Composite Score.
3.  **Safety Gate** -> Rollback if fail.
4.  **Human Review** -> Required if Score > 90.
5.  **Distill** -> Edge Test.
6.  **Release** -> Tag, Snapshot, Proof, DAC.
