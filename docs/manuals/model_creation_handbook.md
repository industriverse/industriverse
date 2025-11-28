# Model Creation Handbook

## Philosophy
**We do not train models.** We encode physics.
Instead of gathering millions of labeled samples, we define:
1.  **EnergyPrior**: An energy function $E(x)$ where lower energy = better state.
2.  **TNN (Thermodynamic Neural Network)**: A dynamics solver (ODE/Hamiltonian) that predicts evolution.

## Workflow
1.  **Define Physics**: Write an `EnergyPrior` class in `src/ebm_lib/priors/`.
2.  **Define Dynamics**: Write a `TNN` class in `src/tnn/`.
3.  **Scaffold DAC**: Use `tools/dac_builder_cli.py` to create the capsule.
4.  **Verify**: Run `pytest` and `demo_fusion_stabilization.py`.

## Key Components
### Energy Prior
```python
class FusionPrior(EnergyPrior):
    def energy(self, x):
        # Penalize deviation from target beta
        return (x - target_beta).pow(2)
```

### TNN Solver
```python
class FusionTNN(nn.Module):
    def forward(self, x, t):
        # Predict plasma evolution
        return -grad_U(x)
```

## Best Practices
*   **Units**: Always use SI units (Kelvin, Pascal, Joules).
*   **Differentiability**: Ensure all operations are differentiable (PyTorch).
*   **Constraints**: Use soft penalties (ReLU) instead of hard clamps for better gradients.
