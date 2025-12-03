# Sovereign Internal Intelligence Architecture (SIIA)

> **"The Code Cortex: A Self-Sovereign, Physics-Grounded Intelligence"**

This document defines the architecture for the **Sovereign Code Foundry (SCF)**, the internal organ responsible for autonomous code generation, evolution, and governance within the Industriverse. It replaces external LLM dependencies with a native, physics-grounded loop of **Energy-Based Diffusion Models (EBDMs)** and **Thermodynamic Neural Networks (TNNs)**.

## 1. Core Philosophy: The Conscious Loop

The system operates on a continuous loop of **Generation → Simulation → Scoring → Refinement**.

*   **Generation (GenN)**: Proposes code/structures.
*   **Simulation (TNN/USM)**: Tests the proposal in a physics-constrained environment.
*   **Scoring (EBDM)**: Assigns an "energy" score (lower is better) based on correctness, efficiency, and safety.
*   **Refinement (Langevin)**: Iteratively improves the proposal by following the energy gradient.

## 2. The Sovereign Code Foundry (SCF) Structure

The SCF is organized into a biological tree structure with 28 specialized modules.

### 🌳 Roots: Context & Memory
*   **`context_root.py`**: The anchor. Loads ACE playbooks, CFR history, and domain knowledge.
*   **`memory_stem.py`**: Long-term storage of success/failure patterns.
*   **`intent_memory_bridge.py`**: Connects past learnings to future intents.
*   **`contextual_regulator.py`**: Safety valve for context injection.

### 🪵 Trunk: Orchestration
*   **`trifecta_master_loop.py`**: The main event loop (Observe-Orient-Decide-Act).
*   **`state_machine.py`**: Manages lifecycle states (Gather -> Gen -> Sim -> Deploy).
*   **`logic_router.py`**: Dispatches tasks to the correct branch.

### 🌿 Branches: Intent, Build, Verify
*   **Intent Branch**:
    *   `intent_engine.py`: Generates specs.
    *   `intent_shaper.py`: Refines specs based on narrative/physics.
    *   `intent_verifier.py`: Governance checks.
    *   `intent_composer.py`: Multi-agent consensus.
*   **Build Branch**:
    *   `builder_engine.py`: Core code synthesis (GenN).
    *   `architecture_generator.py`: System-level design.
    *   `simulation_harness.py`: TNN/USM proxy execution.
    *   `static_analyzer.py`: Code quality/security checks.
    *   `mutation_engine.py`: Evolutionary algorithms.
    *   `refinement_cycle.py`: Feedback loop.
*   **Verify Branch**:
    *   `review_engine.py`: CriticNet analysis.
    *   `deep_verification.py`: Unit/Chaos testing.
    *   `zk_verification_bridge.py`: UZKL proof minting.

### 🍃 Canopy: Deployment
*   **`deployment_strategy.py`**: Target selection (Edge, Cloud, Metaverse).
*   **`bitnet_autodeploy.py`**: 1.58-bit model deployment.
*   **`agent_instantiator.py`**: Spawns new agents from code.

### 🍎 Fertilization: Feedback
*   **`cfr_logger.py`**: Writes to the Cognitive Fossil Record.
*   **`incentive_mapper.py`**: Calculates rewards (Joules/Value).

### 🏛️ Governance: Safety
*   **`safety_regulator.py`**: Meta-safety lattice enforcement.
*   **`ethics_limiter.py`**: Ethical constraints.
*   **`zk_compliance_auditor.py`**: Compliance proofs.

## 3. The Internal Model Engine (The "Ghost" in the Machine)

Instead of calling OpenAI, the SCF modules call these internal models:

### A. EBDM (Energy-Based Diffusion Model)
*   **Role**: The "Judge".
*   **Function**: $E(x, c)$ outputs a scalar energy score for code $x$ under context $c$.
*   **Training**: Contrastive divergence on CFR data (Good Code = Low Energy).

### B. TNN (Thermodynamic Neural Network)
*   **Role**: The "Simulator".
*   **Function**: Predicts the physical/computational cost of executing code.
*   **Constraint**: Enforces conservation of energy in predictions.

### C. GenN (Generator Network)
*   **Role**: The "Scribe".
*   **Function**: Lightweight transformer/RNN that outputs initial code candidates.
*   **Optimization**: Trained to minimize the EBDM energy of its outputs.

### D. CriticNet
*   **Role**: The "Reviewer".
*   **Function**: Multi-head output (Correctness, Efficiency, Security, Novelty).

## 4. Implementation Strategy

1.  **Skeleton Phase**: Create the 28-module Python structure (Interfaces only).
2.  **Bootstrap Phase**: Implement "Mock" internal models that use heuristics or simple rules.
3.  **Training Phase**: Begin collecting data via the Mock system to train the real EBDM/TNNs.
4.  **Sovereign Phase**: Swap Mocks for trained Models.

## 5. Directory Map

```text
src/scf/
├── roots/
├── trunk/
├── branches/
│   ├── intent/
│   ├── build/
│   └── verify/
├── canopy/
│   └── deploy/
├── fertilization/
├── governance/
├── operators/
├── tests/
└── demo/
```
