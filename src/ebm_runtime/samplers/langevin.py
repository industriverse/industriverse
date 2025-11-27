import numpy as np
# import torch
# import jax
# import jax.numpy as jnp

def langevin_step_numpy(x, grad, lr, noise_scale):
    return x - lr * grad + noise_scale * np.random.randn(*x.shape)

# def langevin_step_torch(x, grad, lr, noise_scale):
#     return x - lr * grad + noise_scale * torch.randn_like(x)

# @jax.jit
# def langevin_step_jax(x, grad, lr, noise_scale, key):
#     return x - lr * grad + noise_scale * jax.random.normal(key, x.shape)

def langevin_sample(prior, state, cfg):
    lr = cfg.get("lr", 1e-2)
    steps = cfg.get("steps", 100)
    noise = cfg.get("noise", 0.01)

    backend = cfg.get("backend", "numpy")

    x = state["state_vector"]
    history = []

    for s in range(steps):
        grad = prior.grad({"state_vector": x})["state_vector"]
        if backend == "numpy":
            x = langevin_step_numpy(x, grad, lr, noise)
        # elif backend == "torch":
        #     x = torch.tensor(x)
        #     grad = torch.tensor(grad)
        #     x = langevin_step_torch(x, grad, lr, noise).detach().numpy()
        # elif backend == "jax":
        #     key = jax.random.PRNGKey(s)
        #     x = np.array(langevin_step_jax(jnp.array(x), jnp.array(grad), lr, noise, key))
        else:
             # Fallback to numpy if backend not supported/installed
             x = langevin_step_numpy(x, grad, lr, noise)

        history.append({
            "step": s,
            "energy": prior.energy({"state_vector": x}),
            "state": x.copy()
        })

    return {
        "samples": history,
        "final_state": x,
        "energy_trace": [h["energy"] for h in history]
    }
