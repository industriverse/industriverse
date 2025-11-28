# Wafer Fab EBDM Blueprint

**Purpose:** Sample likely defect proposals in wafer images conditioned on thermal maps.

## 1. Energy Formula
```python
E = alpha * (T_map - T_ref)**2 + beta * high_freq_energy(optical_grad)
```

## 2. File Layout
```
capsules/wafer_ebdm/
  data/thermal/*.npy
  data/optical/*.png
  priors/energy_wafer.npy
  model.py
  train.py
  prin_validator.py
  manifest.yaml
```

## 3. Implementation Steps

### Step 1: Data Prep
Fuse thermal scalar fields and optical gradient energy into a multi-modal prior tensor.

### Step 2: Model
Implement `WaferEBDM` using a U-Net with cross-attention to optical channels.

### Step 3: Training
Loss function: Score matching + thermal energy pullback + pixel consistency.

### Step 4: Validation
PRIN must include `P_novelty` to measure detection of unseen defect morphologies.

### Step 5: Packaging
```bash
iv build-model capsules/wafer_ebdm/
iv capsule build --model capsules/wafer_ebdm/model.pkg
```
