# Fusion EBDM Blueprint

**Purpose:** Model plausible low-energy plasma equilibria and sample coil current settings that stabilize beta.

## 1. Energy Formula
```python
E = 0.5 * rho * (v**2).sum(axis=-1) + 0.5 * (B**2).sum(axis=-1) + P/(1.4-1)
```

## 2. File Layout
```
capsules/fusion_ebdm/
  data/                 # raw HDF5 / preprocessed fields
  priors/energy_map.npy
  model.py
  train.py
  prin_validator.py
  manifest.yaml
```

## 3. Implementation Steps

### Step 1: Data Prep
Run `tools/gen_energy_map_fusion.py` to convert HDF5 plasma fields into `energy_map.npy`.

### Step 2: Model
Implement `FusionEBDM` inheriting from `BaseEBDM`. Use a 3D UNet for the score network.

### Step 3: Training
Loss function:
```python
loss = mse(score, true_score) + 10 * mse(score, -gradE) + 50 * conservation_penalty
```

### Step 4: Validation
Run `prin_validator.py`. Target PRIN > 0.75.

### Step 5: Packaging
```bash
iv build-model capsules/fusion_ebdm/
iv capsule build --model capsules/fusion_ebdm/model.pkg
```
