"""
Wrapper around the THRML entrypoint.
This module isolates third-party dependency and offers a stable interface.
"""

import numpy as np
# placeholder import - real THRML calls go here
# from thrml import GibbsSampler  # example

def sample_from_energy(energy_obj, num_samples=8, temperature=1.0):
    """
    - energy_obj: returned by generate_energy_kernel
    - returns: list of samples: [{'text':str, 'energy_trace': np.array, 'score_est': float}, ...]
    """
    # PSEUDO: call thrml's sampler with energy seed
    samples = []
    for i in range(num_samples):
        # In real implementation call THRML sampler and decode to text/hypothesis
        seed_id = energy_obj.get('meta', {}).get('seed_id', 'anon')
        sample_text = f"<THERMO-HYPOTHESIS-SAMPLE-{i}> seeded_by_{seed_id}"
        
        # Simulate energy trace (lower is better/more stable)
        energy_trace = np.random.rand(100) * (1.0 / (temperature + 1e-6))
        score = float(np.exp(-np.mean(energy_trace)))  # lower energy -> higher score
        
        samples.append({"text": sample_text, "energy_trace": energy_trace, "score_est": score})
    return samples
