"""
High-level API for discovery loop to call THRML features.
Keep this minimal and stable.
"""

from .adapters.thermo_lora_bridge import generate_energy_kernel
from .samplers.thrml_sampler import sample_from_energy
from .utils.energy_io import save_energy_map, load_energy_map

def create_energy_prior_from_lora(lora_path: str, dataset_meta: dict, out_path: str = None):
    """
    1) load LoRA tensors
    2) create JAX-friendly energy kernel seeded by LoRA
    3) optionally save to disk and return path
    Returns: dict with keys: {'energy_path','energy_stats'}
    """
    energy = generate_energy_kernel(lora_path, dataset_meta)
    if out_path:
        save_energy_map(out_path, energy)
        return {"energy_path": out_path, "energy_stats": energy['stats'], "energy_obj": energy}
    return {"energy_obj": energy, "energy_stats": energy['stats']}

def sample_hypotheses_with_thermo(energy, num_samples: int = 8, temperature: float = 1.0):
    """
    Calls THRML/JAX sampler to produce probabilistic hypothesis candidates.
    Returns: list of sample dicts (text, energy_trace, score_estimates)
    """
    samples = sample_from_energy(energy, num_samples=num_samples, temperature=temperature)
    return samples
