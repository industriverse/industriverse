import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class MicrogridPrior(EnergyPrior):
    name = "microgrid_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Microgrid Balancer Prior.
        x: [batch, 3] -> [Generation, Load, Frequency]
        
        Energy = Supply/Demand Mismatch + Frequency Deviation
        """
        gen = x[..., 0]
        load = x[..., 1]
        freq = x[..., 2]
        
        # 1. Power Balance (Gen must match Load)
        # We assume Load is fixed (external), so we optimize Gen to match it.
        # But here x includes both, so the optimizer will try to change both.
        # In a real controller, Load would be an input parameter, not a variable.
        # For this demo, we assume we can shed load or adjust gen.
        e_balance = (gen - load).pow(2)
        
        # 2. Frequency Stability (Target 60 Hz)
        e_freq = (freq - 60.0).pow(2) * 10.0
        
        # 3. Cost Penalty (Minimize Generation if possible, or use efficient sources)
        # Simple proxy: minimize Gen^2 (quadratic cost curve)
        e_cost = 0.01 * gen.pow(2)
        
        return e_balance + e_freq + e_cost

prior = MicrogridPrior()
prior.register()
