# Apparel EBDM Blueprint

**Purpose:** Propose low-energy stitch paths for automated 5-axis sewing minimizing thread tension and material deformation.

## 1. Energy Formula
```python
E = lambda1 * strain_energy(deformation) + lambda2 * tension**2 + lambda3 * contact_penalty
```

## 2. File Layout
```
capsules/apparel_ebdm/
  data/mesh/*.obj
  priors/energy_mesh.npy
  model.py
  train.py
  prin_validator.py
  manifest.yaml
```

## 3. Implementation Steps

### Step 1: Data Prep
Convert mesh parameterization into latent fields.

### Step 2: Model
Diffusion model iteratively refines stitch path coordinates on the mesh.

### Step 3: Training
Enforce conservation rules: total stitch length and number constraints.

### Step 4: Validation
Verify strain energy minimization.

### Step 5: Packaging
```bash
iv build-model capsules/apparel_ebdm/
iv capsule build --model capsules/apparel_ebdm/model.pkg
```
