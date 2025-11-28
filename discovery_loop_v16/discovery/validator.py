"""
OBMI validator extended with THRML energy-aware checks.
PRIN = meta_score*0.4 + content_score*0.4 + obmi_score*0.2 (baseline)
Add energy penalty/bonus term: exp(-ΔE_total / (k * T))
"""

import numpy as np
from systems.thermo_core.thermo_core.utils.metrics import deltaE

K_BOLTZ = 1.380649e-23  # notional; use domain scaling factor instead

def compute_energy_term(energy_trace, kT=1.0):
    if energy_trace is None or len(energy_trace) == 0:
        return 0.0
    de = deltaE(np.array(energy_trace))
    # normalize de to manageable scale (domain-specific).
    norm_de = de / (1.0 + abs(de))
    return np.exp(-norm_de / (kT + 1e-12))

def obmi_scores_from_text(text: str, dataset_meta: dict):
    """
    Existing OBMI computations: AESP, QERO, AROE, AIEO, PRIN base.
    Placeholder returns synthetic scores; replace with real operator calls.
    """
    # TODO: import real operator classes and run them
    return {"AESP": 0.35, "QERO": 4.5, "AROE": 0.8, "AIEO": 0.95, "PRIN_base": 0.70}

def validate_candidates(candidate: dict, dataset_meta: dict, kT: float = 1.0):
    obmi = obmi_scores_from_text(candidate['text'], dataset_meta)
    
    energy_trace = candidate.get('energy_trace')
    if energy_trace is not None:
        energy_term = compute_energy_term(np.array(energy_trace), kT=kT)
    else:
        energy_term = 0.0 # No bonus if no energy trace
        
    pr_base = obmi['PRIN_base']
    # combine
    prin = 0.4 * (dataset_meta.get('meta_score', 0.5)) + \
           0.4 * (pr_base) + \
           0.2 * ( (1 - obmi['AROE']) * 0.5 + obmi['AIEO'] * 0.5 )
    
    # apply energy multiplier (secret-sauce)
    # small boost if energy efficient
    prin_thermo = float(prin * (0.9 + 0.2 * energy_term)) if energy_trace is not None else prin
    
    decision = "APPROVED" if prin_thermo >= 0.75 else ("REVIEW" if prin_thermo >= 0.65 else "REJECT")
    
    return {
        **candidate,
        "metrics": {**obmi, "prin_base": pr_base, "prin_thermo": prin_thermo, "energy_term": float(energy_term)},
        "decision": decision
    }
