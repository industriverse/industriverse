# Thermodynamic ML Foundry (TMF) Playbook

> [!IMPORTANT]
> **Mission:** Convert the 50-demo universe into a repeatable factory for Energy-Based Diffusion Models (EBDMs) and Thermodynamic Neural Networks (TNNs).
> **Goal:** Create physics-grounded, safety-aligned, capsule-ready, proof-capable models.

---

## 🏗 The 7-Layer Mechanism

Every model must pass through these 7 layers:

1.  **Energy Extraction Layer:** Convert dataset to energy map/trajectory.
    *   `E = 0.5*rho*v^2 + ...`
2.  **Thermodynamic Prior Layer:** Integrate dataset as probability prior.
    *   `P(x) = softmax(-E(x) / T)`
3.  **Conservation Law Compiler (CLC):** Auto-generate physical constraints.
    *   `enforce_mass(u)`, `enforce_energy(E_t, E_0)`
4.  **Energy-Conditioned Architecture:** Unified scaffold for EBDM & TNN.
    *   `score_fn - grad(E_prior)`
5.  **PRIN Validator:** Physical Reasoner & Integrity Network scoring.
    *   `PRIN > 0.75` required.
6.  **Proof & UTID Packager:** Self-attesting model artifacts.
    *   `model.utid.json`, `model.energy.sig`
7.  **Capsule Binder:** Auto-wrap into Sovereign Capsule (DAC).
    *   `iv capsule build`

---

## 🧬 Model Blueprints

### A. Energy-Based Diffusion Model (EBDM)
**Concept:** Diffusion models guided by thermodynamic potentials.
**Core Equation:** `score = score_fn(x, t) - grad(E_prior)(x)`
**Use Cases:**
*   **Fusion:** Plasma equilibrium sampling.
*   **Wafer:** Thermal-optical defect generation.
*   **Grid:** Frequency anomaly sampling.

### B. Thermodynamic Neural Network (TNN)
**Concept:** Neural networks with built-in Hamiltonian dynamics.
**Core Equation:** `F = -grad(H_total)`, where `H_total = H_physics + H_learned`
**Use Cases:**
*   **Fusion:** Symplectic integration of plasma state.
*   **Robotics:** Lagrangian mechanics with learned friction.

---

## 🛠 Developer Checklist

- [ ] **Data:** Extract energy map -> `priors/energy_map.npy`
- [ ] **Model:** Implement `model.py` using TMF scaffold.
- [ ] **Train:** Implement training loop with energy pullback.
- [ ] **Validate:** Run `prin_validator.py` (Target: PRIN > 0.75).
- [ ] **Package:** Sign & package model -> `.pkg`.
- [ ] **Deploy:** `iv capsule build` -> Register to `capsule://`.

---

## 🚀 Tools

*   **Scaffold Generator:** `python3 tools/new_ebdm.py --name <name> --domain <domain>`
*   **Base Classes:** `src/tmf/scaffold/ebdm.py`, `src/tmf/scaffold/tnn.py`
