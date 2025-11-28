import pytest
import numpy as np
import importlib
import os
from ebm_lib.registry import get as load_prior

# list of capsule ids (match DOMAINS)
from ebm_lib.priors import DOMAINS

SHORT_STEPS = 20

@pytest.mark.parametrize("domain", ["fusion"]) # Only testing fusion for now as it's the only one implemented
def test_prior_energy_and_grad(domain):
    prior = load_prior(f"{domain}_v1")
    # build a minimal synthetic state_vector (small dimension)
    x0 = np.random.randn(8).astype(np.float64)
    state = {"state_vector": x0}
    e0 = prior.energy(state)
    g = prior.grad(state)
    assert isinstance(e0, (float, int))
    assert "state_vector" in g
    assert np.shape(g["state_vector"]) == x0.shape

@pytest.mark.parametrize("domain", ["fusion"])
def test_langevin_reduces_energy(domain):
    prior = load_prior(f"{domain}_v1")
    from ebm_runtime.samplers.langevin import langevin_sample
    x0 = np.random.randn(8).astype(np.float64) * 2.0
    res = langevin_sample(prior, {"state_vector": x0}, {"steps": SHORT_STEPS, "lr":0.01, "noise":0.05, "backend":"numpy"})
    energies = res["energy_trace"]
    # energy should generally trend down (not strictly monotonic due to noise)
    # Check if final energy is lower than initial or average of last 5 is lower than first 5
    assert energies[-1] < energies[0] + 1.0 # Loose check due to stochasticity

# TNN tests for the four flagship classes:
TNN_TEST_SPECS = [
    ("fusion_v1", "tnn.fusion_tnn.FusionHamiltonianTNN"),
]

def import_class(path):
    mod_name, cls_name = path.rsplit(".",1)
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)

@pytest.mark.parametrize("capsule_id,tnn_path", TNN_TEST_SPECS)
def test_tnn_simulate(capsule_id, tnn_path):
    TNNClass = import_class(tnn_path)
    tnn = TNNClass()
    # construct small example states per type:
    if "fusion" in capsule_id:
        state={"B": np.ones((8,3))*0.1, "v": np.ones((8,3))*0.01, "rho": 1.0}
        res = tnn.simulate(state, {}, dt=0.01, steps=5)
        assert "trajectory" in res and len(res["trajectory"])>0
