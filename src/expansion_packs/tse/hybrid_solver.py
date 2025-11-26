import numpy as np

class HybridSolver:
    """
    Simulates a physical system using a hybrid approach:
    1. Classical PDE Step (Diffusion/Advection)
    2. Neural Correction Step (Mocked)
    """
    def __init__(self, grid_size=10, diffusion_coeff=0.1):
        self.grid_size = grid_size
        self.D = diffusion_coeff
        self.state = np.zeros(grid_size)

    def initialize(self, initial_state):
        if len(initial_state) != self.grid_size:
            raise ValueError(f"Initial state must be size {self.grid_size}")
        self.state = np.array(initial_state, dtype=float)

    def step(self, dt=0.1):
        """
        Advances simulation by dt.
        """
        # 1. Classical Diffusion Step (Finite Difference)
        new_state = np.copy(self.state)
        for i in range(1, self.grid_size - 1):
            # dU/dt = D * d^2U/dx^2
            laplacian = (self.state[i+1] - 2*self.state[i] + self.state[i-1])
            new_state[i] += self.D * laplacian * dt
            
        # 2. Neural Correction (Mock)
        # Simulates a learned correction term (e.g., to account for non-linearities)
        correction = self._neural_correction(new_state)
        new_state += correction * dt
        
        self.state = new_state
        return self.state

    def _neural_correction(self, state):
        # Mock neural net: adds a small non-linear decay term
        # In a real demo, this would call a PyTorch/JAX model
        return -0.01 * (state ** 2)
