"""
Orchestrator for the thermodynamic discovery loop.
Calls: ShadowTwin -> Generator (THRML or LM) -> Validator (OBMI+PRIN+energy) -> Packer (DAC)
"""

import time
import logging
from .generator import generate_candidates
from .validator import validate_candidates
from .capsule_packer import pack_capsule

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_discovery(dataset_meta: dict, lora_path: str, out_dir: str, num_candidates: int = 8):
    t0 = time.time()
    logger.info(f"Starting discovery loop for {dataset_meta.get('dataset_name', 'unknown')}")
    
    # 1) generate (THRML seeded if available)
    logger.info("Generating candidates...")
    candidates = generate_candidates(dataset_meta, lora_path, num_candidates=num_candidates)
    
    # 2) validate each candidate
    logger.info("Validating candidates...")
    validated = []
    for c in candidates:
        v = validate_candidates(c, dataset_meta)
        validated.append(v)
    
    # 3) choose best candidate(s) (by PRIN + energy-efficiency)
    approved = [v for v in validated if v['decision'] == 'APPROVED']
    logger.info(f"Approved {len(approved)}/{len(validated)} candidates")
    
    # 4) pack DACs for approved
    capsules = []
    for a in approved:
        logger.info(f"Packing capsule for approved candidate...")
        capsule_path = pack_capsule(a, out_dir)
        capsules.append(capsule_path)
    
    t1 = time.time()
    duration = t1 - t0
    logger.info(f"Discovery loop completed in {duration:.2f}s")
    
    return {"capsules": capsules, "duration_s": duration, "approved_count": len(approved)}
