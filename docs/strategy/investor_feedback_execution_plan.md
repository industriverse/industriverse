# Investor Feedback Execution Plan: The "Critical 6"

## Objective
Infuse the 6 "Critical" feedback points from the investor audit into the platform to transition from a "Proto-AGI" to an "Invincible Industrial Intelligence System".

## Analysis & Strategy

### 1. Machine Capability Model (MCM)
*   **Feedback**: "Stronger abstraction for real machines."
*   **Gap**: Current drivers are generic. We need a schema that defines torque limits, thermal envelopes, and axis constraints.
*   **Solution**: Implement `MachineCapabilityModel` (Pydantic) to validate intents against physical hardware limits *before* simulation.
*   **Location**: `src/core/machine_capability_model.py`.

### 2. Capsule-to-Capsule Messaging (A2A Bridge)
*   **Feedback**: "Allow Capsules to collaborate like agents."
*   **Gap**: Capsules currently talk to Maestro, not each other.
*   **Solution**: Implement `AgentBus` (A2A Bridge) allowing Capsules to publish "Need" and "Offer" messages directly.
*   **Location**: `src/core/a2a_bridge.py`.

### 3. Skill Trees
*   **Feedback**: "Capsules should learn, publish, and share upgrades."
*   **Gap**: Capsules are static code blocks.
*   **Solution**: Add `SkillTree` to `Capsule` metadata. Skills are versioned, unlockable capabilities (e.g., "High-Speed Milling v2").
*   **Location**: `src/core/skill_tree.py`.

### 4. Zero-Knowledge Capsule Proof (ZKCP)
*   **Feedback**: "Protect IP in Capsule bidding."
*   **Gap**: Bids are currently plaintext.
*   **Solution**: Implement `ZKProofGenerator`. Bids will carry a cryptographic proof that they satisfy the requirements without revealing the proprietary toolpath/recipe.
*   **Location**: `src/security/zk_capsule_proof.py`.

### 5. Live Physics Overlay
*   **Feedback**: "Investors visually feel the physical intelligence."
*   **Gap**: Dashboard shows graphs, but not a "heads-up display" of forces.
*   **Solution**: Add a `PhysicsOverlay` component to the Frontend that renders force vectors and thermal gradients over the machine view.
*   **Location**: `src/frontend/components/PhysicsOverlay.jsx`.

### 6. The 15-Second Highlight Demo
*   **Feedback**: "A single magical clip that sells the AGI Loop instantly."
*   **Gap**: Demos are 1-2 minutes long.
*   **Solution**: Create `scripts/demos/demo_highlight_reel.js` (or Python) that executes a rapid-fire, perfect sequence: Intent -> ZK Bid -> Sim -> Execution -> Profit.
*   **Location**: `src/demos/demo_highlight_reel.js`.

## Execution Steps

### Phase 73: Investor Feedback Infusion

#### Iteration 1: Core Architecture (MCM & A2A)
1.  [ ] Create `src/core/machine_capability_model.py`.
2.  [ ] Create `src/core/a2a_bridge.py`.
3.  [ ] Integrate MCM into `AGIController` (Hardware Check).

#### Iteration 2: Intelligent Capsules (Skills & ZK)
4.  [ ] Create `src/core/skill_tree.py`.
5.  [ ] Create `src/security/zk_capsule_proof.py`.
6.  [ ] Update `Capsule` definition to include Skills and ZK Proofs.

#### Iteration 3: The "Wow" Factor (Frontend & Demo)
7.  [ ] Create `src/frontend/components/PhysicsOverlay.jsx`.
8.  [ ] Integrate Overlay into `DemoDashboard.jsx`.
9.  [ ] Create `src/demos/demo_highlight_reel.js`.

#### Iteration 4: Verification
10. [ ] Run `demo_highlight_reel.js` to verify all new components working in unison.
