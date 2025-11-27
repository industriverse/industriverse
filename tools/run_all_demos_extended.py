import os, yaml, json, time
import numpy as np
from ebm_lib.registry import get as load_prior
import ebm_lib.priors # Force registration
from ebm_runtime.samplers.langevin import langevin_sample
import importlib

# Adjust paths relative to this script
CAPSULE_ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "capsules", "sovereign")
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts", "ebm_tnn_runs")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def load_manifest(capsule_dir):
    with open(os.path.join(capsule_dir,"manifest.yaml")) as f:
        return yaml.safe_load(f)

def import_class(path):
    mod_name, cls_name = path.rsplit(".",1)
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)

def create_initial_state_for_prior(prior, dim=32):
    # default random vector; specific priors can override their expected shape through required_fields
    return {"state_vector": np.random.randn(dim).astype(np.float64)}

caps = [d for d in os.listdir(CAPSULE_ROOT) if os.path.isdir(os.path.join(CAPSULE_ROOT,d))]

report = []
for capsule in sorted(caps):
    capsule_dir = os.path.join(CAPSULE_ROOT, capsule)
    try:
        manifest = load_manifest(capsule_dir)
    except FileNotFoundError:
        print("Skipping", capsule, "(no manifest)")
        continue

    print("=== RUN:", capsule)
    prior_name = manifest.get("energy_prior")
    if not prior_name:
        print("  no prior -> skip")
        continue

    try:
        prior = load_prior(prior_name)
    except ValueError:
        print(f"  Prior {prior_name} not found -> skip")
        continue

    init_state = create_initial_state_for_prior(prior, dim=8) # Small dim for demo

    # run Langevin
    cfg = {"steps": 50, "lr": 0.01, "noise": 0.05, "backend":"numpy"}
    start = time.time()
    res = langevin_sample(prior, init_state, cfg)
    elapsed = time.time() - start

    final_state = res["final_state"].tolist()
    final_energy = float(res["energy_trace"][-1])
    proof = {
        "capsule": capsule,
        "prior": prior_name,
        "final_energy": final_energy,
        "timestamp": time.time(),
        "run_id": f"{capsule}-{int(time.time())}"
    }

    # if TNN present, run simulate with basic mapping
    tnn_res = None
    tnn_class_path = manifest.get("tnn_class")
    if tnn_class_path:
        try:
            TNNClass = import_class(tnn_class_path)
            tnn = TNNClass()
            # build a tiny state mapping heuristics:
            if "fusion" in capsule:
                state={"B": np.random.randn(8,3)*0.1, "v": np.random.randn(8,3)*0.01, "rho":1.0}
            elif "wafer" in capsule:
                state={"temperature_grid": np.random.randn(16,16)}
            elif "apparel" in capsule:
                state={"tension": np.random.rand()*10}
            elif "grid" in capsule:
                state={"frequency": 60.0}
            else:
                state = {"state_vector": np.random.randn(16)}
            tnn_res = tnn.simulate(state, {}, dt=0.05, steps=20)
            # Convert numpy arrays to list for JSON serialization
            if tnn_res and "trajectory" in tnn_res:
                for step in tnn_res["trajectory"]:
                    for k, v in step.items():
                        if isinstance(v, np.ndarray):
                            step[k] = v.tolist()
        except Exception as e:
            print("  TNN run failed for", capsule, e)
            tnn_res = {"error": str(e)}

    # write artifacts
    out = {
        "capsule": capsule,
        "manifest": manifest,
        "proof": proof,
        "ebm": {"final_energy": final_energy, "trace_len": len(res["energy_trace"])},
        "tnn": tnn_res
    }
    out_path = os.path.join(ARTIFACTS_DIR, f"{capsule}.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print("Wrote artifact", out_path)
    report.append({"capsule": capsule, "energy": final_energy, "artifact": out_path, "elapsed": elapsed})

# summary
summary_path = os.path.join(ARTIFACTS_DIR,"summary.json")
with open(summary_path,"w") as f:
    json.dump(report, f, indent=2)
print("Done. Summary ->", summary_path)
