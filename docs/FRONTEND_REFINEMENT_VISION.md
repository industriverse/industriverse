# Frontend Refinement Vision: The Sovereign Interface

## Executive Summary
To support the **FactoryOps 27-Area Expansion** and the **North Star Vision**, the frontend must evolve from a simple dashboard into a **Sovereign Industrial Operating System**. This interface must handle the diversity of 27 distinct industrial domains while maintaining a unified, premium user experience that emphasizes sovereignty, proof, and automation.

## Core Design Pillars
1.  **Sovereign Identity First**: Every interaction is grounded in UTID (Universal Trust ID) and EDCoC (Edge Device Chain of Custody). The UI must visually reinforce that the user is operating a *sovereign* node, not just a SaaS account.
2.  **Dynamic Diversity**: The interface must adapt to 27 different contexts—from a mining pit (Area 1) to a cleanroom lab (Area 19)—using the **DAC Factory** to dynamically render domain-specific widgets without code changes.
3.  **Proof-Centricity**: "Proof" is the product. ASAL proofs, compliance certificates, and audit logs should be first-class UI citizens, not hidden in settings.
4.  **Agentic Collaboration**: The "Trifecta" (UserLM, RND1, ACE) should be omnipresent. The UI is not just a control panel but a *collaboration space* with AI agents.

## Architectural Enhancements

### 1. The "FactoryOps" Dashboard (Scale & Navigation)
*   **Challenge**: Displaying 27+ capsules in a flat list is unmanageable.
*   **Solution**: A **Spatial/Hierarchical Dashboard**.
    *   **Views**:
        *   *Lifecycle View*: Group by "Sourcing" -> "Processing" -> "Assembly" -> "Logistics".
        *   *Spatial View*: A 3D or 2D map of the factory floor (Digital Twin lite).
    *   **Omni-Bar Evolution**: Enhanced natural language command center (e.g., "Show me all active NDT capsules in Sector 4").

### 2. Enhanced DAC Renderer (The "Universal Adapter")
*   **Challenge**: Each of the 27 areas requires unique visualizations (Magnet curves, Thermal heatmaps, Supply chain maps).
*   **Solution**: Expand `DACRenderer.tsx` to support a **Standard Library of Industrial Widgets**.
    *   `StreamPlot`: For real-time sensor data (Area 1, 7, 16).
    *   `Heatmap3D`: For thermal/structural analysis (Area 4, 8, 18).
    *   `GeoMap`: For logistics and mining (Area 1, 21).
    *   `MoleculeViewer`: For chemical/material structures (Area 2, 9, 13).
    *   `ProofCertificate`: A standardized, verifiable display for ASAL proofs.

### 3. The "Pilot" Bridge (Streamlit Integration)
*   **Challenge**: Rapid pilots use Streamlit, but the main app is React.
*   **Solution**: **Seamless Embedding**.
    *   Use `iframe` integration to host Streamlit "Dynamic Islands" directly within the React Capsule Card.
    *   Shared Auth/State between React host and Streamlit guest.

### 4. Sovereign Theming (Whitelabeling)
*   **Challenge**: Partners need their own branding.
*   **Solution**: **Deep Theming Engine**.
    *   Expand `ThemeSwitcher` to support "Brand Kits" (Logo, Primary/Secondary Colors, Typography).
    *   "Glassmorphism" and "Neomorphism" presets for premium industrial aesthetics.

## Implementation Roadmap (Phase 10)

### Step 1: Component Library Expansion
*   Create `src/components/visualizers/IndustrialWidgets/`
*   Implement `Heatmap`, `GeoMap`, `MoleculeViewer` using generic libraries (e.g., `react-three-fiber`, `leaflet`).

### Step 2: Dashboard Refactor
*   Implement `GroupedCapsuleGrid` to handle categorized display.
*   Add "Lifecycle" and "Category" filters to the `Dashboard` state.

### Step 3: Proof UI Polish
*   Create a dedicated `ProofBadge` and `CertificateViewer` component that visually parses the ASAL proof JSON.

### Step 4: Pilot Embedding
*   Create `StreamlitContainer` component for secure iframe embedding.

## User Experience Walkthrough
1.  **Login**: User enters via **UTID Biometric Auth** (simulated).
2.  **Overview**: Sees a high-level "Factory Health" map, aggregated from all 27 areas.
3.  **Drill-Down**: Clicks "Area 12: Magnets".
4.  **Capsule View**: The `DACRenderer` loads the `magnet_assembly_v1` schema.
    *   **Left**: Real-time furnace telemetry (StreamPlot).
    *   **Center**: 3D Magnetic Field Simulation (Three.js).
    *   **Right**: "Optimization Agent" chat (UserLM) and "Proof of Yield" badge.
5.  **Action**: User asks "Optimize for 5% less Dy". RND1 runs, and the 3D sim updates in real-time.
