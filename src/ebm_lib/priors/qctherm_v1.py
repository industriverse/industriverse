import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class ThermalPredPrior(EnergyPrior):
    name = "qctherm_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Thermal Runaway Predictor Prior.
        x: [batch, 2] -> [Surface_Temp, Subsurface_Temp]
        
        Energy = Anomaly Detection (Correlation Break)
        """
        surf = x[..., 0]
        sub = x[..., 1]
        
        # Physics: Surface Temp should be correlated with Subsurface Temp
        # T_surf ~ k * T_sub (Simple conduction model)
        # k = 0.8
        
        expected_surf = 0.8 * sub
        
        # Anomaly: If Surface is cold but Subsurface is hot -> Hidden Defect/Runaway
        e_anomaly = (surf - expected_surf).pow(2)
        
        # Safety Limit: Subsurface shouldn't exceed 100
        e_safety = torch.relu(sub - 100.0) * 100.0
        
        return e_anomaly + e_safety

prior = ThermalPredPrior()
prior.register()
