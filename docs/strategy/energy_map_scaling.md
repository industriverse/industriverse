# Energy Map Scaling Strategy: The 10TB Grounding
**Status**: Draft
**Phase**: 26

## 1. Objective
Transform 10TB of raw, domain-specific physics datasets (HDF5, CSV, Logs) into a unified, queryable **"Energy Landscape"** that serves as the ground truth for all 27 Sovereign Capsules.

## 2. The "Physics Crawler" Pipeline (ETL)
We do not manually load files. We deploy a **Physics Crawler** (`tools/generate_energy_maps.py`) that autonomously builds the Energy Maps.

### Step 1: Ingest (Crawl)
- **Source**: `/Volumes/Expansion` (External Drive).
- **Logic**: Recursive scan for `.hdf5`, `.nc` (NetCDF), `.csv`, `.parquet`.
- **Identification**: Heuristic matching of filenames/metadata to Capsule Domains.
    - `*MHD*`, `*plasma*` -> **Fusion Capsule**
    - `*wafer*`, `*thermal*` -> **Wafer Capsule**
    - `*grid*`, `*frequency*` -> **Grid Capsule**

### Step 2: Extract (Feature Selection)
- **Dimensionality Reduction**: Raw simulation data is often high-dimensional (e.g., 3D Vector Fields + Time).
- **Action**: We extract the **State Variables** relevant to control.
    - Fusion: $B$-field slice at $z=0$ (Stability Plane).
    - Wafer: Surface Temperature Map.
    - Grid: Frequency & Phase Angle vectors.

### Step 3: Normalize (Energy Calibration)
- **Z-Score**: $x' = (x - \mu) / \sigma$
- **Energy Definition**: $E(x) = -\log P(x)$ (Boltzmann).
    - High Probability (Frequent in dataset) = **Low Energy** (Stable).
    - Low Probability (Rare/Absent) = **High Energy** (Unstable).

### Step 4: Compress (The Map)
- **Format**: `.npz` (NumPy Compressed).
- **Content**:
    - `energy_map`: The processed tensor.
    - `metadata`: Source file, timestamp, units.
- **Storage**: `src/ebm_lib/energy_maps/` (Local Cache).

## 3. Scaling to 10TB
- **Lazy Loading**: We do not load 10TB into RAM. We index the files and load specific slices on-demand or pre-compute the Energy Surface using a VAE (Variational Autoencoder) if the data is too large.
- **For Phase 26**: We assume direct extraction is feasible for key slices.

## 4. Value Proposition
This strategy ensures that **"The Map is the Territory."** Our AI doesn't hallucinate physics; it looks up the answer in the 10TB record of reality.
