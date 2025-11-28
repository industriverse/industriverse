"""
Directive 02: Domain Equations
Magnetohydrodynamic (MHD) equations for fusion plasma stability.
"""

import jax
import jax.numpy as jnp

def grad_p(p, dx):
    """Gradient of pressure."""
    return jnp.gradient(p, dx)

def force_balance(p, J, B, dx):
    """
    MHD Force Balance: grad(p) = J x B
    Returns residual (should be zero at equilibrium).
    """
    gp = grad_p(p, dx)
    jxb = jnp.cross(J, B)
    return gp - jxb

def beta_value(p, B):
    """
    Plasma Beta: ratio of plasma pressure to magnetic pressure.
    beta = 2 * mu0 * p / B^2
    """
    mu0 = 1.25663706e-6
    magnetic_pressure = jnp.sum(B**2) / (2 * mu0)
    return jnp.mean(p) / magnetic_pressure

def troyon_limit(I_p, a, B_t):
    """
    Troyon Beta Limit: beta_max = beta_N * I_p / (a * B_t)
    """
    beta_N = 2.8 # Typical value
    return beta_N * I_p / (a * B_t)
