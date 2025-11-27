import numpy as np
from tnn.base import TNN

class FusionHamiltonianTNN(TNN):
    def simulate(self, state, control, dt, steps):
        B = state["B"]   # magnetic field
        v = state["v"]   # plasma velocity
        rho = state["rho"]

        history = []

        for s in range(steps):
            # Simplified MHD equations
            # dB/dt = - curl(E) = curl(v x B) -> simplified as -cross(v, B) for demo
            dB = -np.cross(v, B) * dt 
            
            # dv/dt = (1/rho) * (J x B - grad(p)) -> simplified
            # J = curl(B) -> simplified as gradient(B)
            # This is a toy model for demonstration
            dv = (1 / rho) * np.cross(B, np.gradient(B, axis=0)) * dt

            B = B + dB
            v = v + dv

            history.append({"step": s, "B": B.copy(), "v": v.copy()})

        return {"trajectory": history}
