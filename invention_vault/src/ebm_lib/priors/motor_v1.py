import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class MotorPrior(EnergyPrior):
    name = "motor_v1"
    
    def __init__(self, target_torque=10.0):
        super().__init__()
        self.target_torque = target_torque

    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Motor Harmonics Solver Prior.
        x: [batch, 3] -> [Id, Iq, Speed]
        
        Energy = Torque Error + Efficiency Loss (Id^2)
        """
        # Field Oriented Control (FOC) simplified
        # Torque is proportional to Iq (assuming surface PMSM)
        # Id should be 0 for max efficiency
        
        i_d = x[..., 0]
        i_q = x[..., 1]
        speed = x[..., 2]
        
        # 1. Torque Error (minimize deviation from target)
        # Torque ~ k * i_q
        k_torque = 1.5
        current_torque = k_torque * i_q
        e_torque = (current_torque - self.target_torque).pow(2)
        
        # 2. Efficiency Loss (minimize Id)
        # Id produces heat but no torque
        e_efficiency = 5.0 * i_d.pow(2)
        
        # 3. Speed Stability (penalize extreme fluctuations if we had history, 
        # but here just keep it bounded/regularized)
        e_reg = 0.01 * speed.pow(2)
        
        return e_torque + e_efficiency + e_reg

prior = MotorPrior()
prior.register()
