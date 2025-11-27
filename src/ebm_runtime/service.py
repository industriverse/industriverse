from ebm_lib.registry import get as load_prior
from ebm_runtime.samplers.langevin import langevin_sample
# from ebm_runtime.samplers.diffusion_guided import diffusion_guided_sample # To be implemented

def sample(prior_name, initial_state, sampler):
    prior = load_prior(prior_name)

    if sampler["type"] == "langevin":
        return langevin_sample(prior, initial_state, sampler)

    # if sampler["type"] == "diffusion_guided":
    #     return diffusion_guided_sample(prior, initial_state, sampler)

    raise ValueError("Unknown sampler type.")
