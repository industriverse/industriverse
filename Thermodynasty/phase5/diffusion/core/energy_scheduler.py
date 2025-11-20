"""
Energy-Based Noise Schedulers

Implements various noise schedules for diffusion processes,
including thermodynamically-motivated Boltzmann scheduling.
"""

import torch
import math
from typing import Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class NoiseScheduler(ABC):
    """Base class for noise schedulers"""

    def __init__(
        self,
        timesteps: int,
        beta_start: float,
        beta_end: float,
        device: str = "cpu"
    ):
        self.timesteps = timesteps
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.device = torch.device(device)

        self.betas = self.compute_schedule()
        self.alphas = 1.0 - self.betas

    @abstractmethod
    def compute_schedule(self) -> torch.Tensor:
        """Compute noise schedule"""
        pass


class LinearScheduler(NoiseScheduler):
    """
    Linear noise schedule: β_t increases linearly from β_start to β_end.

    Simple and commonly used in DDPM.
    """

    def compute_schedule(self) -> torch.Tensor:
        """Compute linear schedule"""
        return torch.linspace(
            self.beta_start,
            self.beta_end,
            self.timesteps,
            device=self.device
        )


class CosineScheduler(NoiseScheduler):
    """
    Cosine noise schedule from Nichol & Dhariwal (2021).

    Provides better signal preservation in early steps.
    """

    def __init__(
        self,
        timesteps: int,
        beta_start: float = 0.0001,
        beta_end: float = 0.02,
        s: float = 0.008,
        device: str = "cpu"
    ):
        self.s = s  # Offset parameter
        super().__init__(timesteps, beta_start, beta_end, device)

    def compute_schedule(self) -> torch.Tensor:
        """
        Compute cosine schedule.

        ᾱ_t = cos²((t/T + s)/(1 + s) · π/2)
        β_t = 1 - (ᾱ_t / ᾱ_{t-1})
        """
        steps = self.timesteps
        x = torch.linspace(0, steps, steps + 1, device=self.device)

        alphas_cumprod = torch.cos(
            ((x / steps) + self.s) / (1 + self.s) * math.pi * 0.5
        ) ** 2

        alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
        betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])

        return torch.clip(betas, 0.0001, 0.9999)


class BoltzmannScheduler(NoiseScheduler):
    """
    Boltzmann-weighted noise schedule based on thermodynamic principles.

    β_t ∝ exp(-E_t / kT)

    Where E_t is the "energy" at timestep t (proxy for signal strength).
    Early steps (high noise) have high "temperature" (exploration),
    late steps (low noise) have low "temperature" (refinement).
    """

    def __init__(
        self,
        timesteps: int,
        beta_start: float = 0.0001,
        beta_end: float = 0.02,
        temperature: float = 1.0,
        schedule_type: str = "exponential",  # exponential, sigmoid, power
        device: str = "cpu"
    ):
        """
        Initialize Boltzmann scheduler.

        Args:
            timesteps: Number of diffusion steps
            beta_start: Initial noise level
            beta_end: Final noise level
            temperature: Thermodynamic temperature parameter
            schedule_type: Type of decay (exponential, sigmoid, power)
            device: Computation device
        """
        self.temperature = temperature
        self.schedule_type = schedule_type
        super().__init__(timesteps, beta_start, beta_end, device)

        logger.info(f"Initialized BoltzmannScheduler: T={temperature}, type={schedule_type}")

    def compute_schedule(self) -> torch.Tensor:
        """
        Compute Boltzmann-weighted schedule.

        Different schedule types provide different decay curves.
        """
        t = torch.linspace(0, 1, self.timesteps, device=self.device)

        if self.schedule_type == "exponential":
            # Exponential decay: β_t = β_start + (β_end - β_start) · exp(-t/T)
            weights = torch.exp(-t / self.temperature)

        elif self.schedule_type == "sigmoid":
            # Sigmoid decay: smooth transition
            weights = torch.sigmoid((0.5 - t) / self.temperature)

        elif self.schedule_type == "power":
            # Power-law decay: β_t ∝ (1 - t)^(1/T)
            weights = (1 - t) ** (1.0 / self.temperature)

        else:
            raise ValueError(f"Unknown schedule type: {self.schedule_type}")

        # Normalize to [beta_start, beta_end]
        weights = (weights - weights.min()) / (weights.max() - weights.min() + 1e-8)
        betas = self.beta_start + (self.beta_end - self.beta_start) * (1 - weights)

        return betas

    def energy_at_step(self, t: int) -> float:
        """
        Compute "energy" at timestep t.

        This represents the signal-to-noise ratio or information content.
        Higher energy = more signal, lower energy = more noise.
        """
        beta_t = self.betas[t].item()
        alpha_t = self.alphas[t].item()

        # Energy proxy: log(signal/noise ratio)
        energy = -math.log(beta_t / (alpha_t + 1e-8))

        return energy

    def temperature_at_step(self, t: int) -> float:
        """
        Compute effective temperature at timestep t.

        Early steps: high temperature (exploration)
        Late steps: low temperature (exploitation)
        """
        progress = t / self.timesteps
        effective_temp = self.temperature * (1.0 - progress)

        return effective_temp


class AdaptiveScheduler(NoiseScheduler):
    """
    Adaptive noise schedule that adjusts based on energy field statistics.

    Dynamically modulates β_t based on current energy variance
    to maintain optimal noise levels.
    """

    def __init__(
        self,
        timesteps: int,
        beta_start: float = 0.0001,
        beta_end: float = 0.02,
        adaptation_rate: float = 0.1,
        device: str = "cpu"
    ):
        """
        Initialize adaptive scheduler.

        Args:
            timesteps: Number of steps
            beta_start: Initial beta
            beta_end: Final beta
            adaptation_rate: How fast to adapt (0-1)
            device: Computation device
        """
        self.adaptation_rate = adaptation_rate
        super().__init__(timesteps, beta_start, beta_end, device)

        # Initialize with linear schedule
        self.adaptive_betas = self.betas.clone()

    def compute_schedule(self) -> torch.Tensor:
        """Initial linear schedule"""
        return torch.linspace(
            self.beta_start,
            self.beta_end,
            self.timesteps,
            device=self.device
        )

    def adapt_schedule(self, energy_variance: float, step: int):
        """
        Adapt schedule based on observed energy variance.

        High variance → increase noise (more exploration)
        Low variance → decrease noise (more exploitation)

        Args:
            energy_variance: Current energy field variance
            step: Current timestep
        """
        # Compute target beta based on variance
        # Normalize variance to [0, 1] (assuming variance in [0, 10])
        normalized_var = min(energy_variance / 10.0, 1.0)

        # Target beta: higher variance → higher beta
        target_beta = self.beta_start + (self.beta_end - self.beta_start) * normalized_var

        # Adaptive update with learning rate
        self.adaptive_betas[step] = (
            (1 - self.adaptation_rate) * self.adaptive_betas[step] +
            self.adaptation_rate * target_beta
        )

        # Update alphas
        self.alphas = 1.0 - self.adaptive_betas

    def get_adaptive_betas(self) -> torch.Tensor:
        """Get current adaptive schedule"""
        return self.adaptive_betas


def create_scheduler(
    schedule_type: str,
    timesteps: int,
    beta_start: float = 0.0001,
    beta_end: float = 0.02,
    temperature: float = 1.0,
    device: str = "cpu"
) -> NoiseScheduler:
    """
    Factory function to create noise schedulers.

    Args:
        schedule_type: Type of scheduler (linear, cosine, boltzmann, adaptive)
        timesteps: Number of diffusion steps
        beta_start: Initial noise level
        beta_end: Final noise level
        temperature: Temperature parameter (for Boltzmann)
        device: Computation device

    Returns:
        Noise scheduler instance
    """
    if schedule_type == "linear":
        return LinearScheduler(timesteps, beta_start, beta_end, device)

    elif schedule_type == "cosine":
        return CosineScheduler(timesteps, beta_start, beta_end, device=device)

    elif schedule_type == "boltzmann":
        return BoltzmannScheduler(
            timesteps, beta_start, beta_end,
            temperature=temperature,
            device=device
        )

    elif schedule_type == "adaptive":
        return AdaptiveScheduler(timesteps, beta_start, beta_end, device=device)

    else:
        raise ValueError(f"Unknown schedule type: {schedule_type}")
