import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class RoboticsPrior(EnergyPrior):
    name = "robotics_v1"
    
    def __init__(self, target_pos=None):
        super().__init__()
        # Default target if none provided
        self.default_target = torch.tensor([1.0, 1.0, 1.0]) # x, y, z

    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Robotic Arm Stability Prior.
        x: [batch, 6] -> [pos_x, pos_y, pos_z, vel_x, vel_y, vel_z]
        
        Energy = Position Error + Velocity Damping (Stability)
        """
        # Split state into position and velocity
        pos = x[..., :3]
        vel = x[..., 3:]
        
        target = self.default_target.to(x.device)
        if x.shape[0] > 1:
             target = target.expand(x.shape[0], -1)

        # 1. Position Error (Potential Energy)
        e_pos = 0.5 * (pos - target).pow(2).sum(dim=-1)
        
        # 2. Velocity Damping (Kinetic Energy / Stability)
        # Penalize high velocities to ensure smooth, stable movement
        e_vel = 0.1 * vel.pow(2).sum(dim=-1)
        
        return e_pos + e_vel

prior = RoboticsPrior()
prior.register()
