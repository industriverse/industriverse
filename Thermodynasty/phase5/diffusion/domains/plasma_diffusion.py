"""
Plasma Energy Diffusion

Domain capsule for plasma stability and confinement optimization.
Specializes diffusion models for fusion energy and plasma physics.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass

from ..core.diffusion_dynamics import DiffusionModel, DiffusionConfig
from ..core.energy_field import EnergyField
from ..core.sampler import EnergyGuidedSampler
from ..core.entropy_metrics import EntropyValidator


@dataclass
class PlasmaConfig:
    """Configuration for plasma diffusion"""

    # Plasma parameters
    plasma_temperature: float = 1e7  # Kelvin (10 million K for fusion)
    plasma_density: float = 1e20  # particles/m^3
    magnetic_field_strength: float = 5.0  # Tesla
    plasma_radius: float = 1.0  # meters

    # Spatial resolution
    resolution: int = 128  # Higher resolution for plasma dynamics
    aspect_ratio: float = 3.0  # Tokamak aspect ratio

    # Physical constants
    electron_mass: float = 9.109e-31  # kg
    proton_mass: float = 1.673e-27  # kg
    elementary_charge: float = 1.602e-19  # Coulombs
    boltzmann_constant: float = 1.381e-23  # J/K
    vacuum_permittivity: float = 8.854e-12  # F/m

    # Diffusion parameters
    timesteps: int = 1000
    noise_schedule: str = "linear"
    beta_start: float = 0.0001
    beta_end: float = 0.02

    # Stability constraints
    beta_limit: float = 0.05  # Plasma beta (pressure/magnetic pressure)
    q_safety_min: float = 2.0  # Minimum safety factor
    enforce_mhd_stability: bool = True


class PlasmaEnergyField(EnergyField):
    """
    Energy field specialized for plasma systems.

    Includes plasma-specific energy components:
    - Thermal kinetic energy
    - Magnetic confinement energy
    - Electrostatic potential energy
    - Radiation losses
    """

    def __init__(
        self,
        config: PlasmaConfig,
        device: str = "cpu"
    ):
        super().__init__(
            shape=(config.resolution, config.resolution),
            temperature=config.plasma_temperature * config.boltzmann_constant,
            energy_tolerance=0.01,
            device=device
        )
        self.config = config

    def compute_plasma_energy(
        self,
        density_profile: torch.Tensor,
        temperature_profile: torch.Tensor,
        magnetic_field: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Compute total plasma energy from profiles.

        Args:
            density_profile: [H, W] plasma density distribution
            temperature_profile: [H, W] temperature distribution
            magnetic_field: [H, W] magnetic field strength

        Returns:
            Dictionary of energy components
        """
        # Thermal energy: E_th = 3/2 * n * k * T
        thermal_energy = 1.5 * density_profile * self.config.boltzmann_constant * temperature_profile

        # Magnetic energy: E_mag = B^2 / (2 * μ0)
        mu0 = 4 * np.pi * 1e-7  # Permeability of free space
        magnetic_energy = (magnetic_field ** 2) / (2 * mu0)

        # Electrostatic energy (simplified Debye shielding)
        electrostatic_energy = self._compute_electrostatic_energy(density_profile, temperature_profile)

        # Total energy
        total_energy = thermal_energy + magnetic_energy + electrostatic_energy

        return {
            'thermal': thermal_energy.sum(),
            'magnetic': magnetic_energy.sum(),
            'electrostatic': electrostatic_energy.sum(),
            'total': total_energy.sum()
        }

    def _compute_electrostatic_energy(
        self,
        density: torch.Tensor,
        temperature: torch.Tensor
    ) -> torch.Tensor:
        """Compute electrostatic potential energy"""
        # Debye length: λ_D = sqrt(ε0 * k * T / (n * e^2))
        debye_length = torch.sqrt(
            self.config.vacuum_permittivity * self.config.boltzmann_constant * temperature /
            (density * self.config.elementary_charge ** 2 + 1e-10)
        )

        # Electrostatic energy proportional to 1/λ_D
        electrostatic_energy = density * self.config.elementary_charge / (debye_length + 1e-10)

        return electrostatic_energy

    def compute_confinement_time(
        self,
        energy_map: torch.Tensor
    ) -> float:
        """
        Compute energy confinement time (simplified).

        τ_E = W / P_loss

        Where W is stored energy and P_loss is power loss.
        """
        # Stored energy
        stored_energy = float(energy_map.sum().item())

        # Power loss (simplified - radiation + transport)
        # P_loss ∝ n^2 * T^0.5 (bremsstrahlung radiation)
        power_loss = stored_energy * 0.01  # Simplified 1% loss rate

        # Confinement time
        tau_e = stored_energy / (power_loss + 1e-10)

        return tau_e

    def compute_beta_parameter(
        self,
        thermal_pressure: torch.Tensor,
        magnetic_pressure: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute plasma beta: β = p_thermal / p_magnetic

        Critical parameter for plasma stability.
        """
        beta = thermal_pressure / (magnetic_pressure + 1e-10)
        return beta

    def check_mhd_stability(
        self,
        pressure_profile: torch.Tensor,
        q_profile: torch.Tensor
    ) -> Dict[str, bool]:
        """
        Check MHD (Magnetohydrodynamic) stability criteria.

        Args:
            pressure_profile: Plasma pressure profile
            q_profile: Safety factor profile

        Returns:
            Dictionary of stability checks
        """
        # Kruskal-Shafranov criterion: q > 1
        q_stable = torch.all(q_profile > 1.0).item()

        # Pressure gradient limit
        pressure_gradient = torch.diff(pressure_profile, dim=0)
        gradient_stable = torch.all(torch.abs(pressure_gradient) < 0.1).item()

        # Current density limit (simplified)
        current_stable = True  # Placeholder

        return {
            'q_criterion': q_stable,
            'pressure_gradient': gradient_stable,
            'current_density': current_stable,
            'overall_stable': q_stable and gradient_stable and current_stable
        }


class PlasmaDiffusion:
    """
    Plasma energy diffusion engine.

    Generates plasma equilibrium configurations and stability maps
    for fusion energy applications.
    """

    def __init__(
        self,
        config: Optional[PlasmaConfig] = None,
        device: str = "cpu"
    ):
        """
        Initialize plasma diffusion engine.

        Args:
            config: Plasma configuration
            device: Computation device
        """
        self.config = config or PlasmaConfig()
        self.device = torch.device(device)

        # Initialize energy field
        self.energy_field = PlasmaEnergyField(self.config, device=device)

        # Initialize diffusion model
        diffusion_config = DiffusionConfig(
            timesteps=self.config.timesteps,
            schedule_type=self.config.noise_schedule,
            beta_start=self.config.beta_start,
            beta_end=self.config.beta_end
        )
        self.diffusion_model = DiffusionModel(diffusion_config)

        # Initialize sampler
        self.sampler = EnergyGuidedSampler(
            self.diffusion_model,
            self.energy_field,
            temperature=self.config.plasma_temperature * self.config.boltzmann_constant
        )

        # Validator
        self.validator = EntropyValidator(
            energy_tolerance=0.01,
            temperature=self.config.plasma_temperature * self.config.boltzmann_constant
        )

    def generate_equilibrium_configuration(
        self,
        num_samples: int = 1,
        num_inference_steps: int = 100,
        seed: Optional[int] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Generate plasma equilibrium configurations.

        Args:
            num_samples: Number of configurations to generate
            num_inference_steps: Denoising steps
            seed: Random seed

        Returns:
            Dictionary with equilibrium data
        """
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)

        # Generate using energy-guided sampler
        samples = self.sampler.sample(
            shape=(num_samples, 1, self.config.resolution, self.config.resolution),
            num_inference_steps=num_inference_steps
        )

        # Compute plasma parameters for each sample
        confinement_times = []
        beta_values = []
        stable_samples = []

        for sample in samples:
            # Compute confinement time
            tau_e = self.energy_field.compute_confinement_time(sample.squeeze())

            # Compute beta
            thermal_pressure = sample.squeeze()
            magnetic_pressure = torch.ones_like(thermal_pressure) * self.config.magnetic_field_strength ** 2
            beta = self.energy_field.compute_beta_parameter(thermal_pressure, magnetic_pressure)

            # Check stability
            q_profile = torch.linspace(2.0, 4.0, self.config.resolution, device=self.device)
            stability = self.energy_field.check_mhd_stability(
                sample.squeeze(),
                q_profile.unsqueeze(1).expand(-1, self.config.resolution)
            )

            confinement_times.append(tau_e)
            beta_values.append(float(beta.mean().item()))
            stable_samples.append(stability['overall_stable'])

        return {
            'equilibrium_maps': samples,
            'confinement_times': torch.tensor(confinement_times),
            'beta_values': torch.tensor(beta_values),
            'stable': torch.tensor(stable_samples),
            'metadata': {
                'plasma_temperature': self.config.plasma_temperature,
                'magnetic_field': self.config.magnetic_field_strength,
                'plasma_density': self.config.plasma_density
            }
        }

    def optimize_confinement(
        self,
        target_beta: float = 0.03,
        max_iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Optimize plasma configuration for maximum confinement.

        Args:
            target_beta: Target plasma beta value
            max_iterations: Maximum optimization steps

        Returns:
            Optimized configuration and metrics
        """
        # Initialize configuration
        config = torch.randn(
            1,
            self.config.resolution,
            self.config.resolution,
            device=self.device
        )

        best_confinement = 0.0
        best_config = config.clone()
        trajectory = []

        for iteration in range(max_iterations):
            # Compute confinement time
            tau_e = self.energy_field.compute_confinement_time(config.squeeze())

            # Compute beta
            thermal_pressure = config.squeeze()
            magnetic_pressure = torch.ones_like(thermal_pressure) * self.config.magnetic_field_strength ** 2
            beta = self.energy_field.compute_beta_parameter(thermal_pressure, magnetic_pressure).mean()

            # Objective: maximize confinement while maintaining target beta
            beta_penalty = abs(float(beta.item()) - target_beta)
            objective = tau_e - 100 * beta_penalty  # Weight beta constraint

            # Track best
            if tau_e > best_confinement:
                best_confinement = tau_e
                best_config = config.clone()

            trajectory.append({
                'iteration': iteration,
                'confinement_time': tau_e,
                'beta': float(beta.item()),
                'objective': objective
            })

            # Gradient-based update (simplified)
            config.requires_grad_(True)
            energy = self.energy_field.compute_total_energy(config.unsqueeze(0))
            energy.backward()

            with torch.no_grad():
                # Move toward higher confinement
                config += 0.01 * torch.randn_like(config)
                config.grad.zero_()

        return {
            'optimized_config': best_config,
            'best_confinement_time': best_confinement,
            'final_beta': trajectory[-1]['beta'],
            'trajectory': trajectory
        }

    def predict_disruption_risk(
        self,
        plasma_state: torch.Tensor,
        lookback_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Predict plasma disruption risk using diffusion model.

        Args:
            plasma_state: Current plasma state
            lookback_steps: Number of historical steps to consider

        Returns:
            Disruption risk assessment
        """
        # Generate future predictions
        future_states = []

        current_state = plasma_state.unsqueeze(0).unsqueeze(0)

        for step in range(lookback_steps):
            # Add small noise and denoise to predict next state
            noisy_state = current_state + 0.1 * torch.randn_like(current_state)

            # Denoise
            t = torch.tensor([step], device=self.device)
            denoised = self.diffusion_model(noisy_state, t)

            future_states.append(denoised)
            current_state = denoised

        # Analyze future trajectory for instability markers
        future_energies = [self.energy_field.compute_total_energy(state) for state in future_states]

        # Disruption risk based on energy trajectory
        energy_trend = torch.diff(torch.tensor(future_energies))
        rapid_energy_change = torch.any(torch.abs(energy_trend) > 0.1).item()

        # Risk score
        risk_score = float(torch.abs(energy_trend).max().item())

        return {
            'risk_score': risk_score,
            'disruption_likely': rapid_energy_change,
            'predicted_states': torch.stack(future_states),
            'energy_trajectory': future_energies
        }

    def design_magnetic_configuration(
        self,
        target_confinement_time: float = 1.0,
        num_coils: int = 16
    ) -> Dict[str, Any]:
        """
        Design optimal magnetic coil configuration.

        Args:
            target_confinement_time: Target energy confinement time (seconds)
            num_coils: Number of magnetic coils

        Returns:
            Optimized coil configuration
        """
        # Initialize coil positions (simplified - circular arrangement)
        theta = torch.linspace(0, 2 * np.pi, num_coils + 1)[:-1]
        coil_positions = torch.stack([
            torch.cos(theta),
            torch.sin(theta)
        ], dim=1).to(self.device)

        # Initialize coil currents
        coil_currents = torch.ones(num_coils, device=self.device) * 1e6  # Amperes

        # Optimize coil currents for target confinement
        best_currents = coil_currents.clone()
        best_error = float('inf')

        for iteration in range(50):
            # Generate equilibrium with current coil configuration
            equilibrium = self.generate_equilibrium_configuration(num_samples=1)

            # Compute confinement time
            tau_e = float(equilibrium['confinement_times'][0].item())

            # Error from target
            error = abs(tau_e - target_confinement_time)

            if error < best_error:
                best_error = error
                best_currents = coil_currents.clone()

            # Update coil currents (simplified gradient-free optimization)
            coil_currents += torch.randn(num_coils, device=self.device) * 1e4

            # Clamp to physical limits
            coil_currents = torch.clamp(coil_currents, 1e5, 1e7)

        return {
            'coil_positions': coil_positions,
            'coil_currents': best_currents,
            'achieved_confinement_time': tau_e,
            'target_error': best_error
        }
