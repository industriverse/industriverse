"""
Diffusion Dynamics

Implements forward and reverse diffusion processes with
energy-based guidance and thermodynamic constraints.
"""

import torch
import torch.nn as nn
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
import logging

from .energy_field import EnergyField, EnergyState

logger = logging.getLogger(__name__)


@dataclass
class DiffusionConfig:
    """Configuration for diffusion model"""
    timesteps: int = 1000
    beta_start: float = 0.0001
    beta_end: float = 0.02
    schedule_type: str = "linear"  # linear, cosine, boltzmann
    energy_guidance_scale: float = 1.0
    temperature: float = 1.0
    energy_tolerance: float = 0.01
    device: str = "cpu"


class ForwardDiffusion:
    """
    Forward diffusion process: Add noise progressively.

    q(x_t | x_{t-1}) = N(x_t; √(1-β_t) x_{t-1}, β_t I)

    With energy guidance:
    x_t = √(1-β_t) x_{t-1} + √β_t ε - λ ∇E(x_{t-1})
    """

    def __init__(self, config: DiffusionConfig):
        self.config = config
        self.device = torch.device(config.device)

        # Compute noise schedule
        self.betas = self._get_noise_schedule()
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod_prev = torch.cat([
            torch.ones(1, device=self.device),
            self.alphas_cumprod[:-1]
        ])

        # Square roots for sampling
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)

        logger.info(f"Initialized ForwardDiffusion: T={config.timesteps}, schedule={config.schedule_type}")

    def _get_noise_schedule(self) -> torch.Tensor:
        """Compute noise schedule β_t"""
        if self.config.schedule_type == "linear":
            return torch.linspace(
                self.config.beta_start,
                self.config.beta_end,
                self.config.timesteps,
                device=self.device
            )
        elif self.config.schedule_type == "cosine":
            return self._cosine_beta_schedule()
        elif self.config.schedule_type == "boltzmann":
            return self._boltzmann_beta_schedule()
        else:
            raise ValueError(f"Unknown schedule type: {self.config.schedule_type}")

    def _cosine_beta_schedule(self) -> torch.Tensor:
        """Cosine schedule from Nichol & Dhariwal (2021)"""
        steps = self.config.timesteps
        s = 0.008  # offset
        x = torch.linspace(0, steps, steps + 1, device=self.device)
        alphas_cumprod = torch.cos(((x / steps) + s) / (1 + s) * torch.pi * 0.5) ** 2
        alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
        betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
        return torch.clip(betas, 0.0001, 0.9999)

    def _boltzmann_beta_schedule(self) -> torch.Tensor:
        """
        Boltzmann-weighted schedule: β_t ∝ exp(-t/T).

        Earlier steps have more noise (exploration),
        later steps have less noise (refinement).
        """
        t = torch.linspace(0, 1, self.config.timesteps, device=self.device)
        # Exponential decay
        betas = self.config.beta_start + (self.config.beta_end - self.config.beta_start) * torch.exp(-t / self.config.temperature)
        return betas

    def add_noise(
        self,
        x_0: torch.Tensor,
        t: torch.Tensor,
        noise: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Add noise at timestep t: x_t = √ᾱ_t x_0 + √(1-ᾱ_t) ε

        Args:
            x_0: Original data
            t: Timestep indices [B]
            noise: Optional pre-generated noise

        Returns:
            (noisy_x, noise_used)
        """
        if noise is None:
            noise = torch.randn_like(x_0)

        sqrt_alpha_prod = self.sqrt_alphas_cumprod[t]
        sqrt_one_minus_alpha_prod = self.sqrt_one_minus_alphas_cumprod[t]

        # Reshape for broadcasting
        while len(sqrt_alpha_prod.shape) < len(x_0.shape):
            sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
            sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)

        noisy_x = sqrt_alpha_prod * x_0 + sqrt_one_minus_alpha_prod * noise

        return noisy_x, noise

    def forward_step(
        self,
        x: torch.Tensor,
        t: int,
        energy_field: Optional[EnergyField] = None
    ) -> torch.Tensor:
        """
        Single forward diffusion step with optional energy guidance.

        Args:
            x: Current state
            t: Timestep
            energy_field: Optional energy field for guidance

        Returns:
            Next state x_{t+1}
        """
        beta_t = self.betas[t]
        alpha_t = self.alphas[t]

        # Standard noise
        noise = torch.randn_like(x)

        # Energy guidance term
        if energy_field is not None:
            energy_grad = energy_field.compute_energy_gradient(x)
            # Scale by guidance strength
            energy_term = self.config.energy_guidance_scale * energy_grad
        else:
            energy_term = 0.0

        # Forward step: x_t = √(1-β_t) x_{t-1} + √β_t ε - λ ∇E
        x_next = torch.sqrt(alpha_t) * x + torch.sqrt(beta_t) * noise - energy_term

        return x_next


class ReverseDiffusion:
    """
    Reverse diffusion process: Denoise progressively.

    p_θ(x_{t-1} | x_t) = N(x_{t-1}; μ_θ(x_t, t), Σ_θ(x_t, t))

    With energy guidance:
    x_{t-1} = μ_θ(x_t, t) + σ_t z - λ ∇E(x_t)
    """

    def __init__(
        self,
        forward_diffusion: ForwardDiffusion,
        model: Optional[nn.Module] = None
    ):
        """
        Initialize reverse diffusion.

        Args:
            forward_diffusion: Forward diffusion process
            model: Optional neural network for learned denoising
        """
        self.forward = forward_diffusion
        self.config = forward_diffusion.config
        self.device = forward_diffusion.device

        self.model = model

        # Precompute posterior coefficients
        self.posterior_variance = (
            self.forward.betas *
            (1.0 - self.forward.alphas_cumprod_prev) /
            (1.0 - self.forward.alphas_cumprod)
        )

        self.posterior_log_variance_clipped = torch.log(
            torch.clamp(self.posterior_variance, min=1e-20)
        )

        self.posterior_mean_coef1 = (
            self.forward.betas *
            torch.sqrt(self.forward.alphas_cumprod_prev) /
            (1.0 - self.forward.alphas_cumprod)
        )

        self.posterior_mean_coef2 = (
            (1.0 - self.forward.alphas_cumprod_prev) *
            torch.sqrt(self.forward.alphas) /
            (1.0 - self.forward.alphas_cumprod)
        )

        logger.info("Initialized ReverseDiffusion")

    def predict_start_from_noise(
        self,
        x_t: torch.Tensor,
        t: torch.Tensor,
        noise: torch.Tensor
    ) -> torch.Tensor:
        """
        Predict x_0 from x_t and predicted noise.

        x_0 = (x_t - √(1-ᾱ_t) ε) / √ᾱ_t
        """
        sqrt_alpha_prod = self.forward.sqrt_alphas_cumprod[t]
        sqrt_one_minus_alpha_prod = self.forward.sqrt_one_minus_alphas_cumprod[t]

        while len(sqrt_alpha_prod.shape) < len(x_t.shape):
            sqrt_alpha_prod = sqrt_alpha_prod.unsqueeze(-1)
            sqrt_one_minus_alpha_prod = sqrt_one_minus_alpha_prod.unsqueeze(-1)

        return (x_t - sqrt_one_minus_alpha_prod * noise) / sqrt_alpha_prod

    def posterior_mean_variance(
        self,
        x_0: torch.Tensor,
        x_t: torch.Tensor,
        t: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Compute posterior q(x_{t-1} | x_t, x_0).

        Returns:
            (posterior_mean, posterior_variance, posterior_log_variance)
        """
        coef1 = self.posterior_mean_coef1[t]
        coef2 = self.posterior_mean_coef2[t]

        while len(coef1.shape) < len(x_t.shape):
            coef1 = coef1.unsqueeze(-1)
            coef2 = coef2.unsqueeze(-1)

        posterior_mean = coef1 * x_0 + coef2 * x_t
        posterior_variance = self.posterior_variance[t]
        posterior_log_variance = self.posterior_log_variance_clipped[t]

        return posterior_mean, posterior_variance, posterior_log_variance

    def reverse_step(
        self,
        x_t: torch.Tensor,
        t: int,
        energy_field: Optional[EnergyField] = None,
        clip_denoised: bool = True
    ) -> torch.Tensor:
        """
        Single reverse diffusion step with energy guidance.

        Args:
            x_t: Current noisy state
            t: Timestep
            energy_field: Optional energy field for guidance
            clip_denoised: Whether to clip predicted x_0

        Returns:
            Previous state x_{t-1}
        """
        t_tensor = torch.tensor([t], device=self.device)

        # Predict noise (or use simple gradient if no model)
        if self.model is not None:
            predicted_noise = self.model(x_t, t_tensor)
        else:
            # Simple gradient-based denoising
            if energy_field is not None:
                predicted_noise = energy_field.compute_energy_gradient(x_t)
            else:
                predicted_noise = torch.zeros_like(x_t)

        # Predict x_0
        x_0_pred = self.predict_start_from_noise(x_t, t_tensor, predicted_noise)

        if clip_denoised:
            x_0_pred = torch.clamp(x_0_pred, -1.0, 1.0)

        # Compute posterior mean and variance
        posterior_mean, _, posterior_log_variance = self.posterior_mean_variance(
            x_0_pred, x_t, t_tensor
        )

        # Sample z ~ N(0, I)
        noise = torch.randn_like(x_t) if t > 0 else torch.zeros_like(x_t)

        # Energy guidance
        if energy_field is not None:
            energy_grad = energy_field.compute_energy_gradient(x_t)
            energy_term = self.config.energy_guidance_scale * energy_grad
        else:
            energy_term = 0.0

        # x_{t-1} = μ + σ z - λ ∇E
        x_prev = posterior_mean + torch.exp(0.5 * posterior_log_variance) * noise - energy_term

        return x_prev


class DiffusionModel:
    """
    Complete energy-based diffusion model.

    Combines forward and reverse processes with thermodynamic constraints.
    """

    def __init__(
        self,
        config: DiffusionConfig,
        model: Optional[nn.Module] = None
    ):
        """
        Initialize diffusion model.

        Args:
            config: Diffusion configuration
            model: Optional neural network for learned denoising
        """
        self.config = config
        self.device = torch.device(config.device)

        # Initialize processes
        self.forward_process = ForwardDiffusion(config)
        self.reverse_process = ReverseDiffusion(self.forward_process, model)

        # Energy field for validation
        self.energy_field = EnergyField(
            shape=(64, 64),  # Will be resized as needed
            temperature=config.temperature,
            energy_tolerance=config.energy_tolerance,
            device=config.device
        )

        logger.info("Initialized complete DiffusionModel")

    def diffuse(
        self,
        x_0: torch.Tensor,
        num_steps: Optional[int] = None
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Full forward diffusion to noise.

        Args:
            x_0: Original data
            num_steps: Number of steps (default: config.timesteps)

        Returns:
            (x_T, metrics)
        """
        if num_steps is None:
            num_steps = self.config.timesteps

        # Initialize metrics
        metrics = {
            'energy_drift': [],
            'entropy_changes': []
        }

        # Update energy field
        self.energy_field.from_numpy(x_0.cpu().numpy())
        initial_energy = self.energy_field.current_state.total_energy

        x_t = x_0
        for t in range(num_steps):
            x_t = self.forward_process.forward_step(x_t, t, self.energy_field)

            # Track energy
            current_energy = float(x_t.sum().item())
            energy_drift = abs(current_energy - initial_energy)
            metrics['energy_drift'].append(energy_drift)

        return x_t, metrics

    def denoise(
        self,
        x_T: torch.Tensor,
        num_steps: Optional[int] = None,
        use_energy_guidance: bool = True
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Full reverse diffusion from noise to data.

        Args:
            x_T: Noisy data
            num_steps: Number of steps (default: config.timesteps)
            use_energy_guidance: Whether to use energy guidance

        Returns:
            (x_0, metrics)
        """
        if num_steps is None:
            num_steps = self.config.timesteps

        # Initialize metrics
        metrics = {
            'energy_drift': [],
            'entropy_changes': [],
            'energy_fidelity': []
        }

        # Energy field for guidance
        energy_field = self.energy_field if use_energy_guidance else None

        x_t = x_T
        for t in reversed(range(num_steps)):
            x_t = self.reverse_process.reverse_step(x_t, t, energy_field)

            # Validate conservation
            if energy_field is not None:
                energy_field.update_state(x_t)
                metrics['energy_drift'].append(energy_field.current_state.metadata['energy_drift'])

        # Final validation
        if energy_field is not None:
            final_state = energy_field.current_state
            metrics['final_energy'] = final_state.total_energy
            metrics['final_entropy'] = final_state.entropy

        return x_t, metrics

    def sample(
        self,
        shape: Tuple[int, ...],
        num_inference_steps: Optional[int] = None
    ) -> torch.Tensor:
        """
        Sample from the diffusion model.

        Args:
            shape: Output shape
            num_inference_steps: Number of denoising steps

        Returns:
            Generated sample
        """
        # Start from pure noise
        x_T = torch.randn(shape, device=self.device)

        # Denoise
        x_0, _ = self.denoise(x_T, num_inference_steps)

        return x_0

    def __repr__(self) -> str:
        return (
            f"DiffusionModel(T={self.config.timesteps}, "
            f"schedule={self.config.schedule_type}, "
            f"device={self.config.device})"
        )
