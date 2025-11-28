"""
Directive 02: Domain Equations
Power flow and thermal constraints for grid immunity.
"""

import math

def active_power(V, I, phi):
    """P = V * I * cos(phi)"""
    return V * I * math.cos(phi)

def reactive_power(V, I, phi):
    """Q = V * I * sin(phi)"""
    return V * I * math.sin(phi)

def check_thermal_limit(I_line, I_max):
    """Returns True if line current is within thermal limits."""
    return abs(I_line) <= I_max

def check_voltage_stability(V_bus, V_nominal, tolerance=0.05):
    """Returns True if bus voltage is within tolerance."""
    return abs(V_bus - V_nominal) <= (V_nominal * tolerance)
