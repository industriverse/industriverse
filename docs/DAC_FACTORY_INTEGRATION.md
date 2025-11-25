# DAC Factory Integration Plan

## Goal Description
Integrate the "Ambient Intelligence" features (MediaPipe, TouchDesigner, Adaptive UX) from the `manus` and `claude` branches into the `feature/final-form-integration` branch. This connects the **Sovereign Capsules** (Backend Physics) with the **DACs** (Frontend Interaction), realizing the full "DAC Factory" vision.

## User Review Required
- **Merge Strategy**: We will merge `manus/week9-day7-completion` and `claude/refine-discovery-loop...` into the main branch.
- **Value Proposition**: This integration enables "Zero Hardware" interaction (MediaPipe) and "Living Data Art" (TouchDesigner) for all 27 capsules.

## Proposed Changes

### 1. Merge "Ambient Intelligence" Features
- **Source**: `origin/manus/week9-day7-completion`
    - Feature: **Adaptive UX Engine** (A/B Testing, Dynamic Layouts).
- **Source**: `origin/claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11`
    - Feature: **MediaPipe Integration** (Gesture Control).
    - Feature: **TouchDesigner Integration** (Generative Visualization).

### 2. Connect to Sovereign Capsules
- **Backend**: `BridgeAPI` (`/v1/capsules`)
- **Frontend**: Update `CapsuleCard` and `Dashboard` to use the new `MediaPipe` gesture controls and `TouchDesigner` visuals.

### 3. The "DAC Factory" Pipeline
This integration establishes the full value extraction pipeline for clients:
1.  **Hypothesis**: User defines a problem (e.g., "Optimize Polymer Flow").
2.  **Physics**: `Sovereign Capsule` (JAX) is instantiated to solve it.
3.  **Interface**: `DAC` (MediaPipe/TouchDesigner) is generated for interaction.
4.  **Delivery**: Client receives a "Sovereign DAC" - a self-contained unit of Physics + UI.

## Verification Plan
### Automated Tests
- Run existing tests from `manus` branch (referenced as "34 comprehensive tests").

### Manual Verification
- **Gesture Control**: Verify webcam interaction with `EnergyField`.
- **Visuals**: Verify `TouchDesigner` assets load for capsules.
