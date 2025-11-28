"""
Load/save lightweight energy maps used as priors.
Format: .npz containing 'field', 'stats', 'meta'
"""

import numpy as np
import os

def save_energy_map(path: str, energy_obj: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez_compressed(path,
                        field=energy_obj['field'],
                        stats=energy_obj.get('stats', {}),
                        meta=energy_obj.get('meta', {}))
    return path

def load_energy_map(path: str):
    data = np.load(path, allow_pickle=True)
    return {"field": data['field'], "stats": data['stats'].item() if 'stats' in data else {}, "meta": data['meta'].item() if 'meta' in data else {}}

def build_energy_object(grad_vector, dataset_meta):
    # simple example building a 2D field from gradient vector
    side = int(np.ceil(len(grad_vector) ** 0.5))
    field = np.zeros((side, side))
    field.flat[:len(grad_vector)] = grad_vector
    meta = {"seed_id": dataset_meta.get("dataset_name", "anon"), "shape": field.shape}
    stats = {"mean": float(field.mean()), "std": float(field.std())}
    return {"field": field, "meta": meta, "stats": stats}
