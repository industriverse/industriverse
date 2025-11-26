# Grid EBDM Blueprint

**Purpose:** Sample and propose low-energy control actions (generator dispatch, storage usage) that return grid frequency to nominal.

## 1. Energy Formula
```python
E = sum(0.5 * M_i * omega_i**2) + sum(supply_costs)
```

## 2. File Layout
```
capsules/grid_ebdm/
  dataset/power_traces/
  priors/grid_energy.npy
  model.py
  train.py
  prin_validator.py
  manifest.yaml
```

## 3. Implementation Steps

### Step 1: Data Prep
Time-series data of frequency deviations and power flows.

### Step 2: Model
Score network over sequences (Time-series diffusion).

### Step 3: Training
Conservation: Power balance per timestep (Generation = Load + Losses).

### Step 4: Validation
PRIN includes `P_coherence` measured as post-control frequency variance reduction.

### Step 5: Packaging
```bash
iv build-model capsules/grid_ebdm/
iv capsule build --model capsules/grid_ebdm/model.pkg
```
