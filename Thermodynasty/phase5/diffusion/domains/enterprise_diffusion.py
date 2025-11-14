"""
Enterprise Energy Diffusion

Domain capsule for compute resource optimization and workflow scheduling.
Specializes diffusion models for datacenter energy management and task allocation.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..core.diffusion_dynamics import DiffusionModel, DiffusionConfig
from ..core.energy_field import EnergyField
from ..core.sampler import EnergyGuidedSampler
from ..core.entropy_metrics import EntropyValidator


@dataclass
class EnterpriseConfig:
    """Configuration for enterprise diffusion"""

    # Compute infrastructure
    num_nodes: int = 100
    num_gpus_per_node: int = 8
    cpu_cores_per_node: int = 64
    memory_per_node: int = 512  # GB

    # Energy parameters
    power_per_gpu: float = 300.0  # Watts
    power_per_cpu: float = 150.0  # Watts
    cooling_efficiency: float = 1.4  # PUE (Power Usage Effectiveness)
    electricity_cost: float = 0.12  # USD per kWh

    # Workload characteristics
    avg_task_duration: float = 3600.0  # seconds
    task_priority_levels: int = 5
    sla_latency_threshold: float = 60.0  # seconds

    # Spatial resolution
    resolution: int = 32  # Grid resolution for resource map

    # Diffusion parameters
    timesteps: int = 500
    noise_schedule: str = "linear"
    beta_start: float = 0.0001
    beta_end: float = 0.02

    # Optimization constraints
    max_node_utilization: float = 0.95
    min_node_utilization: float = 0.20
    enforce_sla: bool = True
    enable_carbon_aware: bool = True


class EnterpriseEnergyField(EnergyField):
    """
    Energy field specialized for enterprise compute systems.

    Includes enterprise-specific energy components:
    - Compute energy (CPU + GPU)
    - Cooling energy
    - Network transfer energy
    - Storage I/O energy
    - Carbon footprint
    """

    def __init__(
        self,
        config: EnterpriseConfig,
        device: str = "cpu"
    ):
        super().__init__(
            shape=(config.resolution, config.resolution),
            temperature=1.0,  # Abstract temperature for compute
            energy_tolerance=0.01,
            device=device
        )
        self.config = config

    def compute_total_power_consumption(
        self,
        cpu_utilization: torch.Tensor,
        gpu_utilization: torch.Tensor,
        network_utilization: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Compute total power consumption from utilization profiles.

        Args:
            cpu_utilization: [H, W] CPU utilization (0-1)
            gpu_utilization: [H, W] GPU utilization (0-1)
            network_utilization: [H, W] network utilization (0-1)

        Returns:
            Dictionary of power components
        """
        # CPU power
        cpu_power = cpu_utilization * self.config.power_per_cpu * self.config.cpu_cores_per_node

        # GPU power
        gpu_power = gpu_utilization * self.config.power_per_gpu * self.config.num_gpus_per_node

        # Network power (simplified)
        network_power = network_utilization * 50.0  # Watts per link

        # Compute power
        compute_power = cpu_power + gpu_power + network_power

        # Cooling power (PUE factor)
        cooling_power = compute_power * (self.config.cooling_efficiency - 1.0)

        # Total power
        total_power = compute_power + cooling_power

        return {
            'cpu': cpu_power.sum(),
            'gpu': gpu_power.sum(),
            'network': network_power.sum(),
            'cooling': cooling_power.sum(),
            'total': total_power.sum()
        }

    def compute_energy_cost(
        self,
        power_consumption: torch.Tensor,
        duration: float = 3600.0
    ) -> float:
        """
        Compute energy cost in USD.

        Args:
            power_consumption: Total power in Watts
            duration: Time period in seconds

        Returns:
            Cost in USD
        """
        # Convert to kWh
        energy_kwh = (power_consumption * duration) / (3600.0 * 1000.0)

        # Cost
        cost = float(energy_kwh * self.config.electricity_cost)

        return cost

    def compute_carbon_footprint(
        self,
        power_consumption: torch.Tensor,
        duration: float = 3600.0,
        carbon_intensity: float = 0.4  # kg CO2/kWh
    ) -> float:
        """
        Compute carbon footprint.

        Args:
            power_consumption: Total power in Watts
            duration: Time period in seconds
            carbon_intensity: Grid carbon intensity (kg CO2/kWh)

        Returns:
            Carbon emissions in kg CO2
        """
        # Convert to kWh
        energy_kwh = (power_consumption * duration) / (3600.0 * 1000.0)

        # Carbon footprint
        carbon_kg = float(energy_kwh * carbon_intensity)

        return carbon_kg

    def compute_resource_fragmentation(
        self,
        allocation_map: torch.Tensor
    ) -> float:
        """
        Compute resource fragmentation score.

        High fragmentation = inefficient resource usage.

        Args:
            allocation_map: Resource allocation map

        Returns:
            Fragmentation score (0-1, lower is better)
        """
        # Compute spatial entropy of allocation
        # High entropy = high fragmentation
        allocation_flat = allocation_map.flatten()
        allocation_flat = allocation_flat / (allocation_flat.sum() + 1e-10)

        # Shannon entropy
        entropy = -torch.sum(allocation_flat * torch.log(allocation_flat + 1e-10))

        # Normalize to [0, 1]
        max_entropy = np.log(allocation_flat.shape[0])
        fragmentation = float(entropy / max_entropy)

        return fragmentation


class EnterpriseDiffusion:
    """
    Enterprise compute energy diffusion engine.

    Optimizes datacenter resource allocation and workflow scheduling
    using thermodynamically-grounded diffusion models.
    """

    def __init__(
        self,
        config: Optional[EnterpriseConfig] = None,
        device: str = "cpu"
    ):
        """
        Initialize enterprise diffusion engine.

        Args:
            config: Enterprise configuration
            device: Computation device
        """
        self.config = config or EnterpriseConfig()
        self.device = torch.device(device)

        # Initialize energy field
        self.energy_field = EnterpriseEnergyField(self.config, device=device)

        # Initialize diffusion model
        diffusion_config = DiffusionConfig(
            timesteps=self.config.timesteps,
            noise_schedule=self.config.noise_schedule,
            beta_start=self.config.beta_start,
            beta_end=self.config.beta_end
        )
        self.diffusion_model = DiffusionModel(diffusion_config)

        # Initialize sampler
        self.sampler = EnergyGuidedSampler(
            self.diffusion_model,
            self.energy_field,
            temperature=1.0  # Abstract temperature for scheduling
        )

        # Validator
        self.validator = EntropyValidator(
            energy_tolerance=0.01,
            temperature=1.0
        )

    def optimize_resource_allocation(
        self,
        workload_profile: torch.Tensor,
        num_samples: int = 10,
        num_inference_steps: int = 50
    ) -> Dict[str, Any]:
        """
        Optimize resource allocation for given workload.

        Args:
            workload_profile: [H, W] workload intensity map
            num_samples: Number of allocation strategies to generate
            num_inference_steps: Optimization steps

        Returns:
            Optimized allocation strategy
        """
        # Generate allocation strategies
        samples = self.sampler.sample(
            shape=(num_samples, 1, self.config.resolution, self.config.resolution),
            num_inference_steps=num_inference_steps
        )

        # Evaluate each strategy
        best_allocation = None
        best_score = float('inf')
        strategies = []

        for sample in samples:
            allocation = sample.squeeze()

            # Normalize to [0, 1] utilization
            allocation = torch.sigmoid(allocation)

            # Clamp to utilization bounds
            allocation = torch.clamp(
                allocation,
                self.config.min_node_utilization,
                self.config.max_node_utilization
            )

            # Compute metrics
            power = self.energy_field.compute_total_power_consumption(
                cpu_utilization=allocation,
                gpu_utilization=allocation * 0.7,  # Assume 70% GPU usage
                network_utilization=allocation * 0.3
            )

            fragmentation = self.energy_field.compute_resource_fragmentation(allocation)
            cost = self.energy_field.compute_energy_cost(power['total'])

            # Combined score (minimize power and fragmentation)
            score = float(power['total'].item()) + 1000 * fragmentation

            strategies.append({
                'allocation': allocation,
                'power_consumption': power,
                'fragmentation': fragmentation,
                'cost_per_hour': cost,
                'score': score
            })

            if score < best_score:
                best_score = score
                best_allocation = allocation

        return {
            'best_allocation': best_allocation,
            'best_score': best_score,
            'all_strategies': strategies,
            'power_savings': strategies[0]['power_consumption']['total'] - strategies[-1]['power_consumption']['total']
        }

    def schedule_workload(
        self,
        tasks: List[Dict[str, Any]],
        time_horizon: float = 3600.0
    ) -> Dict[str, Any]:
        """
        Schedule workload tasks across compute infrastructure.

        Args:
            tasks: List of tasks with requirements
            time_horizon: Scheduling time horizon (seconds)

        Returns:
            Optimized schedule
        """
        # Create task energy map
        task_map = torch.zeros(
            (self.config.resolution, self.config.resolution),
            device=self.device
        )

        for task in tasks:
            # Map task to grid position based on requirements
            compute_intensity = task.get('compute_intensity', 0.5)
            priority = task.get('priority', 0.5)

            # Place task in map
            x = int(compute_intensity * self.config.resolution)
            y = int(priority * self.config.resolution)
            x = min(x, self.config.resolution - 1)
            y = min(y, self.config.resolution - 1)

            task_map[y, x] += 1.0

        # Optimize allocation
        allocation_result = self.optimize_resource_allocation(
            workload_profile=task_map,
            num_samples=5
        )

        # Create schedule
        schedule = []
        allocated_nodes = allocation_result['best_allocation']

        for idx, task in enumerate(tasks):
            # Find best node for task
            compute_intensity = task.get('compute_intensity', 0.5)
            priority = task.get('priority', 0.5)

            x = int(compute_intensity * self.config.resolution)
            y = int(priority * self.config.resolution)
            x = min(x, self.config.resolution - 1)
            y = min(y, self.config.resolution - 1)

            node_utilization = float(allocated_nodes[y, x].item())

            schedule.append({
                'task_id': task.get('task_id', idx),
                'node_assignment': (x, y),
                'start_time': idx * 10.0,  # Simplified scheduling
                'estimated_duration': task.get('duration', self.config.avg_task_duration),
                'node_utilization': node_utilization
            })

        return {
            'schedule': schedule,
            'total_power_consumption': allocation_result['best_score'],
            'estimated_cost': allocation_result['all_strategies'][0]['cost_per_hour'],
            'resource_efficiency': 1.0 - allocation_result['all_strategies'][0]['fragmentation']
        }

    def predict_power_demand(
        self,
        historical_utilization: List[torch.Tensor],
        forecast_horizon: int = 24
    ) -> Dict[str, Any]:
        """
        Predict future power demand using diffusion model.

        Args:
            historical_utilization: List of past utilization maps
            forecast_horizon: Hours to forecast

        Returns:
            Power demand forecast
        """
        # Use recent history as conditioning
        if len(historical_utilization) > 0:
            recent_state = historical_utilization[-1].unsqueeze(0).unsqueeze(0).to(self.device)
        else:
            recent_state = torch.randn(1, 1, self.config.resolution, self.config.resolution, device=self.device)

        # Generate future predictions
        predictions = []
        current_state = recent_state

        for hour in range(forecast_horizon):
            # Add noise and denoise to predict next state
            noisy_state = current_state + 0.05 * torch.randn_like(current_state)

            # Denoise using diffusion model
            t = torch.tensor([0], device=self.device)  # Use t=0 for prediction
            predicted_state = self.diffusion_model(noisy_state, t)

            # Compute power demand
            power = self.energy_field.compute_total_power_consumption(
                cpu_utilization=predicted_state.squeeze(),
                gpu_utilization=predicted_state.squeeze() * 0.7,
                network_utilization=predicted_state.squeeze() * 0.3
            )

            predictions.append({
                'hour': hour,
                'utilization_map': predicted_state,
                'total_power': float(power['total'].item()),
                'cpu_power': float(power['cpu'].item()),
                'gpu_power': float(power['gpu'].item())
            })

            current_state = predicted_state

        return {
            'forecast': predictions,
            'peak_power': max(p['total_power'] for p in predictions),
            'average_power': sum(p['total_power'] for p in predictions) / len(predictions)
        }

    def carbon_aware_scheduling(
        self,
        tasks: List[Dict[str, Any]],
        carbon_intensity_forecast: List[float]
    ) -> Dict[str, Any]:
        """
        Schedule tasks to minimize carbon footprint.

        Args:
            tasks: List of tasks to schedule
            carbon_intensity_forecast: Hourly carbon intensity (kg CO2/kWh)

        Returns:
            Carbon-optimized schedule
        """
        # Find low-carbon time windows
        carbon_intensity_tensor = torch.tensor(carbon_intensity_forecast, device=self.device)
        low_carbon_hours = torch.argsort(carbon_intensity_tensor)[:len(tasks) // 2]

        # Schedule high-priority tasks during low-carbon periods
        sorted_tasks = sorted(tasks, key=lambda t: t.get('priority', 0.5), reverse=True)

        schedule = []
        total_carbon = 0.0

        for idx, task in enumerate(sorted_tasks):
            # Assign to low-carbon hour if available
            if idx < len(low_carbon_hours):
                hour = int(low_carbon_hours[idx].item())
            else:
                hour = idx % len(carbon_intensity_forecast)

            carbon_intensity = carbon_intensity_forecast[hour]

            # Estimate task energy
            task_power = task.get('compute_intensity', 0.5) * 1000.0  # Watts
            task_duration = task.get('duration', self.config.avg_task_duration)
            task_carbon = self.energy_field.compute_carbon_footprint(
                torch.tensor(task_power),
                duration=task_duration,
                carbon_intensity=carbon_intensity
            )

            total_carbon += task_carbon

            schedule.append({
                'task_id': task.get('task_id', idx),
                'scheduled_hour': hour,
                'carbon_intensity': carbon_intensity,
                'estimated_carbon': task_carbon
            })

        return {
            'schedule': schedule,
            'total_carbon_footprint': total_carbon,
            'carbon_savings': sum(carbon_intensity_forecast) / len(carbon_intensity_forecast) * len(tasks) - total_carbon
        }

    def optimize_cooling_efficiency(
        self,
        datacenter_layout: torch.Tensor,
        target_pue: float = 1.2
    ) -> Dict[str, Any]:
        """
        Optimize datacenter cooling for target PUE.

        Args:
            datacenter_layout: [H, W] heat distribution
            target_pue: Target Power Usage Effectiveness

        Returns:
            Optimized cooling strategy
        """
        # Generate cooling configurations
        samples = self.sampler.sample(
            shape=(10, 1, self.config.resolution, self.config.resolution),
            num_inference_steps=50
        )

        best_cooling = None
        best_pue = float('inf')

        for sample in samples:
            cooling_map = torch.sigmoid(sample.squeeze())

            # Compute effective PUE
            # PUE = (IT Power + Cooling Power) / IT Power
            it_power = datacenter_layout.sum()
            cooling_power = cooling_map.sum() * 0.4 * it_power  # Simplified cooling model

            pue = (it_power + cooling_power) / (it_power + 1e-10)
            pue_value = float(pue.item())

            if abs(pue_value - target_pue) < abs(best_pue - target_pue):
                best_pue = pue_value
                best_cooling = cooling_map

        return {
            'cooling_strategy': best_cooling,
            'achieved_pue': best_pue,
            'target_pue': target_pue,
            'pue_error': abs(best_pue - target_pue)
        }
