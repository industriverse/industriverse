# Dataset Manifest: Production Drive

**Location:** `/Volumes/Expansion/industriverse-datasets` & `/Volumes/Expansion/industriverse_datasets`

## 1. Physics & Thermodynamics
*   **`calphad/`**: Calculation of Phase Diagrams. Likely thermodynamic properties of alloys.
    *   *Target:* Material Science / Alloy Design.
*   **`energyflow/`**: Particle Physics (Energy Flow Polynomials).
    *   *Target:* High-energy physics modeling, entropy flow.
*   **`openkim/`**: Knowledgebase of Interatomic Models.
    *   *Target:* Molecular Dynamics.

## 2. Industrial & Manufacturing
*   **`slice100k/`**: 100,000 3D printing slices (G-code/Images).
    *   *Target:* Additive Manufacturing optimization.
*   **`ton_iot/`**: IIoT (Industrial IoT) telemetry and network traffic.
    *   *Target:* Cyber-physical security, anomaly detection.

## 3. Geophysics & Energy
*   **`openfwi/`**: Full Waveform Inversion (Seismic).
    *   *Target:* Subsurface exploration, geothermal.
*   **`the_well/`**: Likely well logs or reservoir data.
    *   *Target:* Energy extraction.

## 4. Existing Artifacts
*   **`energy_atlas_v1.h5`**: A pre-existing Energy Atlas. Needs inspection.

## Ingestion Strategy
1.  **Slice100k**: Extract G-code (LCODE precursor) and layer images.
2.  **EnergyFlow**: Extract 4-vectors (Energy, Momentum) for entropy training.
3.  **Calphad**: Extract Gibbs Free Energy curves.
