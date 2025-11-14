"""
Diffusion Samplers

Implements various sampling strategies for diffusion models,
including energy-guided sampling with thermodynamic constraints.
"""

import torch
from typing import Optional, Callable, Dict, Any, List
from abc import ABC, abstractmethod
import logging

from .energy_field import EnergyField

logger = logging.getLogger(__name__)


class DiffusionSampler(ABC):
    """Base class for diffusion samplers"""

    def __init__(
        self,
        num_inference_steps: int = 50,
        energy_guidance_scale: float = 1.0,
        device: str = "cpu"
    ):
        """
        Initialize sampler.

        Args:
            num_inference_steps: Number of denoising steps
            energy_guidance_scale: Strength of energy guidance
            device: Computation device
        """
        self.num_inference_steps = num_inference_steps
        self.energy_guidance_scale = energy_guidance_scale
        self.device = torch.device(device)

    @abstractmethod
    def sample(
        self,
        model_fn: Callable,
        shape: tuple,
        energy_field: Optional[EnergyField] = None,
        **kwargs
    ) -> torch.Tensor:
        """
        Sample from diffusion model.

        Args:
            model_fn: Function that predicts noise given (x_t, t)
            shape: Output shape
            energy_field: Optional energy field for guidance
            **kwargs: Additional arguments

        Returns:
            Generated sample
        """
        pass


class DDPMSampler(DiffusionSampler):
    """
    Denoising Diffusion Probabilistic Model (DDPM) sampler.

    Implements the standard DDPM sampling algorithm from Ho et al. (2020).
    """

    def __init__(
        self,
        num_inference_steps: int = 1000,
        energy_guidance_scale: float = 1.0,
        clip_sample: bool = True,
        device: str = "cpu"
    ):
        """
        Initialize DDPM sampler.

        Args:
            num_inference_steps: Number of denoising steps
            energy_guidance_scale: Energy guidance strength
            clip_sample: Whether to clip samples to [-1, 1]
            device: Computation device
        """
        super().__init__(num_inference_steps, energy_guidance_scale, device)
        self.clip_sample = clip_sample

    def sample(
        self,
        model_fn: Callable,
        shape: tuple,
        betas: torch.Tensor,
        energy_field: Optional[EnergyField] = None,
        return_all_timesteps: bool = False
    ) -> torch.Tensor:
        """
        DDPM sampling.

        Args:
            model_fn: Noise prediction function
            shape: Output shape
            betas: Noise schedule
            energy_field: Optional energy guidance
            return_all_timesteps: Return all intermediate steps

        Returns:
            Generated sample (or list of all timesteps)
        """
        # Start from pure noise
        x = torch.randn(shape, device=self.device)

        alphas = 1.0 - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)

        all_samples = [x] if return_all_timesteps else None

        # Reverse diffusion
        for t in reversed(range(self.num_inference_steps)):
            t_tensor = torch.full((shape[0],), t, device=self.device, dtype=torch.long)

            # Predict noise
            predicted_noise = model_fn(x, t_tensor)

            # Compute coefficients
            alpha_t = alphas[t]
            alpha_prod_t = alphas_cumprod[t]
            beta_t = betas[t]

            # Predict x_0
            pred_original_sample = (x - torch.sqrt(1 - alpha_prod_t) * predicted_noise) / torch.sqrt(alpha_prod_t)

            if self.clip_sample:
                pred_original_sample = torch.clamp(pred_original_sample, -1.0, 1.0)

            # Compute x_{t-1}
            pred_sample_direction = torch.sqrt(1 - alpha_prod_t) * predicted_noise
            x_prev = torch.sqrt(alpha_t) * (x - pred_sample_direction) / torch.sqrt(alpha_prod_t)

            # Add noise (except at last step)
            if t > 0:
                noise = torch.randn_like(x)
                variance = beta_t
                x_prev = x_prev + torch.sqrt(variance) * noise

            # Energy guidance
            if energy_field is not None:
                energy_grad = energy_field.compute_energy_gradient(x_prev)
                x_prev = x_prev - self.energy_guidance_scale * energy_grad

            x = x_prev

            if return_all_timesteps:
                all_samples.append(x)

        return all_samples if return_all_timesteps else x


class DDIMSampler(DiffusionSampler):
    """
    Denoising Diffusion Implicit Model (DDIM) sampler.

    Faster sampling with deterministic transitions (Song et al., 2020).
    """

    def __init__(
        self,
        num_inference_steps: int = 50,
        eta: float = 0.0,  # 0 = deterministic, 1 = DDPM
        energy_guidance_scale: float = 1.0,
        device: str = "cpu"
    ):
        """
        Initialize DDIM sampler.

        Args:
            num_inference_steps: Number of steps (can be << T)
            eta: Stochasticity parameter (0 = deterministic)
            energy_guidance_scale: Energy guidance strength
            device: Computation device
        """
        super().__init__(num_inference_steps, energy_guidance_scale, device)
        self.eta = eta

    def sample(
        self,
        model_fn: Callable,
        shape: tuple,
        alphas_cumprod: torch.Tensor,
        energy_field: Optional[EnergyField] = None
    ) -> torch.Tensor:
        """
        DDIM sampling (accelerated).

        Args:
            model_fn: Noise prediction function
            shape: Output shape
            alphas_cumprod: Cumulative alpha products
            energy_field: Optional energy guidance

        Returns:
            Generated sample
        """
        # Start from noise
        x = torch.randn(shape, device=self.device)

        # Create timestep schedule (can skip steps)
        timesteps = torch.linspace(
            len(alphas_cumprod) - 1, 0,
            self.num_inference_steps,
            device=self.device
        ).long()

        for i, t in enumerate(timesteps):
            t_tensor = torch.full((shape[0],), t, device=self.device, dtype=torch.long)

            # Predict noise
            predicted_noise = model_fn(x, t_tensor)

            # Get alpha values
            alpha_prod_t = alphas_cumprod[t]
            alpha_prod_t_prev = alphas_cumprod[t - 1] if t > 0 else torch.tensor(1.0)

            # Predict x_0
            pred_original_sample = (
                x - torch.sqrt(1 - alpha_prod_t) * predicted_noise
            ) / torch.sqrt(alpha_prod_t)

            # Compute variance
            variance = self.eta * torch.sqrt(
                (1 - alpha_prod_t_prev) / (1 - alpha_prod_t) *
                (1 - alpha_prod_t / alpha_prod_t_prev)
            )

            # Compute direction
            pred_sample_direction = torch.sqrt(1 - alpha_prod_t_prev - variance ** 2) * predicted_noise

            # Compute x_{t-1}
            x_prev = torch.sqrt(alpha_prod_t_prev) * pred_original_sample + pred_sample_direction

            # Add noise
            if self.eta > 0 and t > 0:
                noise = torch.randn_like(x)
                x_prev = x_prev + variance * noise

            # Energy guidance
            if energy_field is not None:
                energy_grad = energy_field.compute_energy_gradient(x_prev)
                x_prev = x_prev - self.energy_guidance_scale * energy_grad

            x = x_prev

        return x


class EnergyGuidedSampler(DiffusionSampler):
    """
    Energy-guided diffusion sampler with Boltzmann weighting.

    Samples trajectories that minimize energy while respecting
    entropy constraints.
    """

    def __init__(
        self,
        num_inference_steps: int = 50,
        energy_guidance_scale: float = 2.0,
        temperature: float = 1.0,
        num_proposals: int = 5,
        device: str = "cpu"
    ):
        """
        Initialize energy-guided sampler.

        Args:
            num_inference_steps: Number of steps
            energy_guidance_scale: Energy guidance strength
            temperature: Boltzmann temperature
            num_proposals: Number of candidate samples per step
            device: Computation device
        """
        super().__init__(num_inference_steps, energy_guidance_scale, device)
        self.temperature = temperature
        self.num_proposals = num_proposals

        logger.info(
            f"Initialized EnergyGuidedSampler: "
            f"steps={num_inference_steps}, T={temperature}, proposals={num_proposals}"
        )

    def sample(
        self,
        model_fn: Callable,
        shape: tuple,
        energy_field: EnergyField,
        alphas_cumprod: torch.Tensor,
        return_trajectory: bool = False
    ) -> torch.Tensor:
        """
        Energy-guided sampling with Boltzmann selection.

        At each step, generates multiple proposals and selects
        the one with lowest energy (Boltzmann-weighted).

        Args:
            model_fn: Noise prediction function
            shape: Output shape
            energy_field: Energy field for guidance (required)
            alphas_cumprod: Cumulative alpha products
            return_trajectory: Return full sampling trajectory

        Returns:
            Generated sample (lowest energy)
        """
        # Start from noise
        x = torch.randn(shape, device=self.device)

        trajectory = [x] if return_trajectory else None

        timesteps = torch.linspace(
            len(alphas_cumprod) - 1, 0,
            self.num_inference_steps,
            device=self.device
        ).long()

        for t in timesteps:
            # Generate multiple proposals
            proposals = []
            energies = []

            for _ in range(self.num_proposals):
                # Standard DDIM step
                t_tensor = torch.full((shape[0],), t, device=self.device, dtype=torch.long)
                predicted_noise = model_fn(x, t_tensor)

                alpha_prod_t = alphas_cumprod[t]
                alpha_prod_t_prev = alphas_cumprod[t - 1] if t > 0 else torch.tensor(1.0)

                # Predict x_0
                pred_original = (
                    x - torch.sqrt(1 - alpha_prod_t) * predicted_noise
                ) / torch.sqrt(alpha_prod_t)

                # Direction
                pred_direction = torch.sqrt(1 - alpha_prod_t_prev) * predicted_noise

                # Proposal
                proposal = torch.sqrt(alpha_prod_t_prev) * pred_original + pred_direction

                # Add small exploration noise
                if t > 0:
                    proposal = proposal + 0.1 * torch.randn_like(proposal)

                # Compute energy
                energy = energy_field.compute_entropy(proposal)

                proposals.append(proposal)
                energies.append(energy)

            # Boltzmann selection
            energies_tensor = torch.tensor(energies, device=self.device)
            weights = energy_field.boltzmann_weight(energies_tensor)

            # Sample according to Boltzmann distribution
            selected_idx = torch.multinomial(weights, 1).item()
            x = proposals[selected_idx]

            if return_trajectory:
                trajectory.append(x)

        return trajectory if return_trajectory else x


class AncestralSampler(DiffusionSampler):
    """
    Ancestral sampling for diffusion models.

    Uses the full stochastic chain with ancestor resampling.
    """

    def sample(
        self,
        model_fn: Callable,
        shape: tuple,
        betas: torch.Tensor,
        energy_field: Optional[EnergyField] = None
    ) -> torch.Tensor:
        """
        Ancestral sampling.

        Args:
            model_fn: Noise prediction
            shape: Output shape
            betas: Noise schedule
            energy_field: Optional guidance

        Returns:
            Generated sample
        """
        x = torch.randn(shape, device=self.device)

        alphas = 1.0 - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)

        for t in reversed(range(len(betas))):
            t_tensor = torch.full((shape[0],), t, device=self.device, dtype=torch.long)

            # Predict noise
            noise_pred = model_fn(x, t_tensor)

            # Ancestral step
            alpha_t = alphas[t]
            alpha_prod_t = alphas_cumprod[t]

            # Mean
            mean = (x - (1 - alpha_t) / torch.sqrt(1 - alpha_prod_t) * noise_pred) / torch.sqrt(alpha_t)

            # Variance
            if t > 0:
                noise = torch.randn_like(x)
                sigma_t = torch.sqrt(betas[t])
                x = mean + sigma_t * noise
            else:
                x = mean

            # Energy guidance
            if energy_field is not None:
                energy_grad = energy_field.compute_energy_gradient(x)
                x = x - self.energy_guidance_scale * energy_grad

        return x
