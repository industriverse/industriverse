from typing import Dict, List, Callable, Any
import logging
import math

logger = logging.getLogger(__name__)

class DomainEquationPack:
    """
    Registry of domain-specific physics equations for the 27 Capsules.
    Allows capsules to 'consult' their governing laws during reasoning.
    """
    
    def __init__(self):
        self._equations: Dict[str, Callable] = {}
        self._register_defaults()

    def _register_defaults(self):
        # --- Category A: High Energy ---
        self.register("Granular stress models", lambda sigma, phi: sigma * math.tan(math.radians(phi))) # Mohr-Coulomb simplified
        self.register("Arrhenius diffusion", lambda D0, Q, R, T: D0 * math.exp(-Q / (R * T)))
        self.register("Heat equation", lambda k, A, dT, dx: -k * A * (dT / dx)) # Fourier's Law
        
        # --- Category B: Flow/Heat ---
        self.register("Bernoulli equation", lambda P, rho, v, g, h: P + 0.5 * rho * v**2 + rho * g * h)
        self.register("Stefan condition", lambda L, rho, dx_dt: L * rho * dx_dt) # Heat flux discontinuity
        
        # --- Category C: Swarm ---
        self.register("EOQ", lambda D, S, H: math.sqrt((2 * D * S) / H)) # Economic Order Quantity
        
        # --- Category D: Multi-physics ---
        self.register("Entropy production", lambda J, X: J * X) # Flux * Force
        self.register("Weibull distribution", lambda x, k, lam: (k / lam) * ((x / lam)**(k - 1)) * math.exp(-(x / lam)**k))

    def register(self, name: str, func: Callable):
        self._equations[name] = func

    def solve(self, equation_name: str, **kwargs) -> Any:
        """
        Solve a specific equation with provided parameters.
        """
        if equation_name not in self._equations:
            logger.warning(f"Equation '{equation_name}' not found in pack.")
            return None
        
        try:
            return self._equations[equation_name](**kwargs)
        except TypeError as e:
            logger.error(f"Invalid arguments for '{equation_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Error solving '{equation_name}': {e}")
            return None

    def get_equation_names(self) -> List[str]:
        return list(self._equations.keys())
