# S-REAN: Sovereign Rare Earth Acceleration Network

## The Strategic Imperative
The **Sovereign Rare Earth Acceleration Network (S-REAN)** is the "Killer App" of the FactoryOps ecosystem. Its sole purpose is to break the dependency on foreign rare earth supply chains by optimizing the entire lifecycle of critical materials (Neodymium, Dysprosium, Terbium) within a sovereign network.

## The Critical Path (The "Quad")
S-REAN connects four specific Sovereign Capsules into a tight feedback loop:

1.  **Area 1: Raw Material Sourcing** (`raw_material_sourcing_v1`)
    *   **Role**: Identify and certify sovereign ore/feedstock.
    *   **Key Metric**: Provenance Confidence Score.
2.  **Area 2: Rare Earth Refining** (`rare_earth_refining_v1`)
    *   **Role**: Optimize separation efficiency to maximize yield of heavy rare earths.
    *   **Key Metric**: Separation Factor / Reagent Cost.
3.  **Area 12: Magnet Assembly** (`magnet_assembly_v1`)
    *   **Role**: Reduce heavy rare earth usage (Dy/Tb) via Grain Boundary Diffusion (GBD) and microstructure engineering (M2N2).
    *   **Key Metric**: Dy% Reduction (Target: < 1%).
4.  **Area 23: Waste & Recycling** (`waste_management_v1`)
    *   **Role**: Recover magnet scrap and end-of-life motors for "Urban Mining."
    *   **Key Metric**: Recovery Rate.

## The Acceleration Loop
The **Trifecta** drives this network:
*   **UserLM**: Orchestrates the handoffs between capsules (e.g., notifying Area 12 of a new batch from Area 2).
*   **RND1**: Optimizes the *entire chain* simultaneously. For example, it might suggest slightly lower purity from Area 2 if Area 12's new microstructure model can handle it, reducing overall cost and energy.
*   **ACE**: Maintains the "Sovereignty Context," ensuring all data and proofs remain within the trusted network.

## Technical Architecture
*   **Shared Ledger**: A private ledger (or shared database partition) tracks the "Mass Balance" of rare earths across the network.
*   **Orchestrator**: A dedicated service (`s_rean_orchestrator.py`) that subscribes to events from the 4 capsules and triggers cross-capsule optimizations.
*   **Sovereignty Score**: A composite metric calculated in real-time:
    $$ S = \frac{Internal\_Supply + Recycled\_Supply}{Total\_Demand} \times (1 - \frac{Dy\_Content}{Target\_Dy}) $$

## Deployment Strategy
1.  **Phase 1**: Simulation (Current). Connect the 4 blueprints in a virtual loop.
2.  **Phase 2**: Pilot. Deploy Area 12 (Magnets) physically, simulate the rest.
3.  **Phase 3**: Full Network. Deploy all 4 areas with physical partners.
