"""
Create a Deployable AI Capsule (DAC) package with UTID lineage and energy metadata.
Output: DAC package directory or compressed .dacpkg
"""

import json
import os
from .utid import make_utid
from systems.thermo_core.thermo_core.utils.energy_io import save_energy_map

def pack_capsule(validated_candidate: dict, out_dir: str):
    utid = make_utid(validated_candidate)
    capsule_dir = os.path.join(out_dir, utid)
    os.makedirs(capsule_dir, exist_ok=True)

    # write hypothesis
    with open(os.path.join(capsule_dir, "hypothesis.md"), "w") as f:
        f.write(validated_candidate['text'])

    # energy map
    energy_trace = validated_candidate.get('energy_trace')
    if energy_trace is not None:
        energy_path = os.path.join(capsule_dir, "energy.npz")
        # use systems.thermo_core.utils.energy_io to save properly if field is ndarray
        try:
            # Reconstruct a simple energy object for saving
            energy_obj = {
                "field": energy_trace, 
                "stats": validated_candidate.get('energy_stats', {}), 
                "meta": {"seed": utid}
            }
            save_energy_map(energy_path, energy_obj)
        except Exception:
            # fallback small json
            with open(os.path.join(capsule_dir, "energy.json"), "w") as f:
                json.dump({"energy": list(energy_trace)}, f)

    # write metrics + metadata
    metadata = {
        "utid": utid,
        "metrics": validated_candidate.get('metrics', {}),
        "source": validated_candidate.get('source', 'unknown'),
        "lora_path": validated_candidate.get('lora_path', None)
    }
    with open(os.path.join(capsule_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # optional: sign + compress
    package_path = os.path.join(out_dir, f"{utid}.dacpkg")
    # In production, use python tarfile module instead of os.system for safety/portability
    os.system(f"tar -czf {package_path} -C {capsule_dir} .")
    return package_path
