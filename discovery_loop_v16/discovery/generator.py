"""
Generator pipeline:
 - Primary: THRML sample -> decode -> LM refine (optional)
 - Fallback: Local LLM (UserLM/Mistral/instructable) if THRML fails
"""

import logging
from systems.thermo_core.thermo_core.api import create_energy_prior_from_lora, sample_hypotheses_with_thermo

logger = logging.getLogger(__name__)

def generate_candidates(dataset_meta: dict, lora_path: str, num_candidates: int = 8, temperature: float = 0.7):
    # attempt thermo path first
    try:
        logger.info("Attempting thermodynamic generation...")
        res = create_energy_prior_from_lora(lora_path, dataset_meta, out_path=None)
        energy = res.get("energy_obj") or res
        samples = sample_hypotheses_with_thermo(energy, num_samples=num_candidates, temperature=temperature)
        # decode / postprocess: call LM refine to convert short thermo-text to full structured hypothesis
        final = []
        for s in samples:
            # secret sauce: call LM for structure filling with energy trace context
            refined = lm_refine_sample(s['text'], energy_meta=energy.get('meta', {}))
            final.append({
                "text": refined,
                "energy_trace": s['energy_trace'],
                "energy_stats": energy.get('stats', {}),
                "score_est": s['score_est'],
                "source": "thermo",
                "dataset": dataset_meta.get('dataset_name', 'unknown'),
                "lora_path": lora_path
            })
        return final
    except Exception as e:
        logger.error(f"Thermo generation failed: {e}. Falling back to LM.")
        # fallback to LM-only generation
        return fallback_generate_lm(dataset_meta, num_candidates)

def lm_refine_sample(raw_text: str, energy_meta: dict):
    """
    Minimal LM invocation placeholder:
    Purpose: expand / rewrite sample into 5-section hypothesis with numbers + validation clause.
    """
    # TODO: call local LM (UserLM-8b or fallback) with prompt seeded by raw_text + energy_meta
    return f"REFINED HYPOTHESIS based on {raw_text}\n\n1. Abstract: ...\n2. Methodology: ...\n3. Expected Results: ...\n4. Validation: ...\n5. Impact: ..."

def fallback_generate_lm(dataset_meta: dict, num_candidates: int):
    """
    Fallback generator using standard LM approach without energy priors.
    """
    candidates = []
    for i in range(num_candidates):
        candidates.append({
            "text": f"FALLBACK HYPOTHESIS {i} for {dataset_meta.get('dataset_name')}",
            "source": "lm_fallback",
            "dataset": dataset_meta.get('dataset_name', 'unknown')
        })
    return candidates
