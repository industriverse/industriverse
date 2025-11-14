"""
Industriverse Diffusion Framework SDK

Python SDK for programmatic access to energy-based diffusion models,
training pipelines, and deployment infrastructure.

Example Usage:

    from industriverse_sdk import IndustriverseClient

    # Initialize client
    client = IndustriverseClient(api_url="http://localhost:8000")

    # Generate molecular structures
    result = client.molecular.generate(num_samples=10)

    # Optimize enterprise resources
    allocation = client.enterprise.optimize(workload_map=data)

    # Train custom diffusion model
    trainer = client.training.create_trainer(domain="plasma")
    trainer.train(epochs=100)
"""

import requests
import numpy as np
import torch
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class DiffusionResult:
    """Result from diffusion operation"""

    samples: np.ndarray
    energies: Optional[np.ndarray] = None
    metrics: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None


class MolecularAPI:
    """Molecular diffusion operations"""

    def __init__(self, base_url: str, session: requests.Session):
        self.base_url = base_url
        self.session = session

    def generate(
        self,
        num_samples: int = 1,
        num_inference_steps: int = 100,
        seed: Optional[int] = None
    ) -> DiffusionResult:
        """
        Generate molecular equilibrium structures.

        Args:
            num_samples: Number of structures to generate
            num_inference_steps: Number of denoising steps
            seed: Random seed for reproducibility

        Returns:
            DiffusionResult with generated structures
        """
        response = self.session.post(
            f"{self.base_url}/v1/domains/molecular/generate",
            json={
                "num_samples": num_samples,
                "num_inference_steps": num_inference_steps,
                "seed": seed
            }
        )
        response.raise_for_status()

        data = response.json()

        return DiffusionResult(
            samples=np.array([]),  # Energy maps not returned in summary response
            energies=np.array(data['energies']),
            metrics={
                'valid_structures': data['valid_structures'],
                'processing_time_ms': data['processing_time_ms']
            },
            metadata={'domain': 'molecular'}
        )

    def optimize_structure(
        self,
        initial_structure: Optional[np.ndarray] = None,
        max_iterations: int = 100,
        tolerance: float = 0.01
    ) -> DiffusionResult:
        """
        Optimize molecular structure to local energy minimum.

        Args:
            initial_structure: Starting structure (if None, random)
            max_iterations: Maximum optimization steps
            tolerance: Convergence tolerance

        Returns:
            Optimized structure
        """
        # This would call a custom optimization endpoint
        raise NotImplementedError("Structure optimization endpoint not yet available")


class PlasmaAPI:
    """Plasma diffusion operations"""

    def __init__(self, base_url: str, session: requests.Session):
        self.base_url = base_url
        self.session = session

    def generate_equilibrium(
        self,
        num_samples: int = 1,
        num_inference_steps: int = 100,
        seed: Optional[int] = None
    ) -> DiffusionResult:
        """
        Generate plasma equilibrium configurations.

        Args:
            num_samples: Number of configurations to generate
            num_inference_steps: Number of denoising steps
            seed: Random seed for reproducibility

        Returns:
            DiffusionResult with equilibrium configurations
        """
        response = self.session.post(
            f"{self.base_url}/v1/domains/plasma/equilibrium",
            json={
                "num_samples": num_samples,
                "num_inference_steps": num_inference_steps,
                "seed": seed
            }
        )
        response.raise_for_status()

        data = response.json()

        return DiffusionResult(
            samples=np.array([]),  # Maps not returned in summary
            metrics={
                'confinement_times': data['confinement_times'],
                'beta_values': data['beta_values'],
                'stable_configurations': data['stable_configurations'],
                'processing_time_ms': data['processing_time_ms']
            },
            metadata={'domain': 'plasma'}
        )

    def predict_disruption_risk(
        self,
        plasma_state: np.ndarray,
        lookback_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Predict plasma disruption risk.

        Args:
            plasma_state: Current plasma state
            lookback_steps: Number of historical steps

        Returns:
            Disruption risk assessment
        """
        # This would call a custom prediction endpoint
        raise NotImplementedError("Disruption prediction endpoint not yet available")


class EnterpriseAPI:
    """Enterprise diffusion operations"""

    def __init__(self, base_url: str, session: requests.Session):
        self.base_url = base_url
        self.session = session

    def optimize(
        self,
        workload_map: Union[np.ndarray, List[List[float]]],
        num_strategies: int = 10,
        num_inference_steps: int = 50
    ) -> DiffusionResult:
        """
        Optimize datacenter resource allocation.

        Args:
            workload_map: Workload intensity map
            num_strategies: Number of strategies to evaluate
            num_inference_steps: Optimization steps

        Returns:
            Optimized allocation strategy
        """
        if isinstance(workload_map, np.ndarray):
            workload_map = workload_map.tolist()

        response = self.session.post(
            f"{self.base_url}/v1/domains/enterprise/optimize",
            json={
                "workload_intensity": workload_map,
                "num_strategies": num_strategies,
                "num_inference_steps": num_inference_steps
            }
        )
        response.raise_for_status()

        data = response.json()

        return DiffusionResult(
            samples=np.array([]),
            metrics={
                'power_consumption_watts': data['power_consumption_watts'],
                'fragmentation_score': data['fragmentation_score'],
                'cost_per_hour_usd': data['cost_per_hour_usd'],
                'power_savings_watts': data['power_savings_watts'],
                'processing_time_ms': data['processing_time_ms']
            },
            metadata={'domain': 'enterprise'}
        )

    def forecast_power_demand(
        self,
        historical_utilization: List[np.ndarray],
        forecast_horizon: int = 24
    ) -> Dict[str, Any]:
        """
        Forecast future power demand.

        Args:
            historical_utilization: List of past utilization maps
            forecast_horizon: Hours to forecast

        Returns:
            Power demand forecast
        """
        # This would call a custom forecasting endpoint
        raise NotImplementedError("Power forecasting endpoint not yet available")


class TrainingAPI:
    """Training and model management"""

    def __init__(self, base_url: str, session: requests.Session):
        self.base_url = base_url
        self.session = session

    def create_trainer(
        self,
        domain: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Create a training session.

        Args:
            domain: Energy domain (molecular, plasma, enterprise)
            config: Training configuration

        Returns:
            Trainer instance
        """
        # This would integrate with local training
        raise NotImplementedError("Training API not yet available via REST")

    def list_models(self) -> List[Dict[str, Any]]:
        """List available trained models"""
        # This would call a model registry endpoint
        raise NotImplementedError("Model registry not yet available")


class IndustriverseClient:
    """
    Main client for Industriverse Diffusion Framework.

    Provides access to all diffusion operations, training, and deployment.

    Example:
        client = IndustriverseClient(api_url="http://localhost:8000")

        # Generate molecular structures
        result = client.molecular.generate(num_samples=10)
        print(f"Generated {result.metrics['valid_structures']} valid structures")

        # Optimize enterprise resources
        workload = np.random.rand(32, 32)
        allocation = client.enterprise.optimize(workload_map=workload)
        print(f"Power consumption: {allocation.metrics['power_consumption_watts']} W")
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 300
    ):
        """
        Initialize Industriverse client.

        Args:
            api_url: Base URL for API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout

        # Create session
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

        # Initialize API modules
        self.molecular = MolecularAPI(self.api_url, self.session)
        self.plasma = PlasmaAPI(self.api_url, self.session)
        self.enterprise = EnterpriseAPI(self.api_url, self.session)
        self.training = TrainingAPI(self.api_url, self.session)

    def health(self) -> Dict[str, Any]:
        """Check API health status"""
        response = self.session.get(f"{self.api_url}/health", timeout=10)
        response.raise_for_status()
        return response.json()

    def optimize_energy(
        self,
        initial_state: Optional[np.ndarray] = None,
        target_energy: Optional[float] = None,
        max_iterations: int = 100,
        tolerance: float = 0.01,
        method: str = "boltzmann"
    ) -> DiffusionResult:
        """
        Find equilibrium state via energy minimization.

        Args:
            initial_state: Initial energy state
            target_energy: Target energy level
            max_iterations: Maximum optimization iterations
            tolerance: Energy convergence tolerance
            method: Optimization method (gradient, boltzmann, annealing)

        Returns:
            Optimized energy state
        """
        payload = {
            "max_iterations": max_iterations,
            "tolerance": tolerance,
            "method": method
        }

        if initial_state is not None:
            payload['initial_state'] = initial_state.tolist()

        if target_energy is not None:
            payload['target_energy'] = target_energy

        response = self.session.post(
            f"{self.api_url}/v1/optimize",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()

        return DiffusionResult(
            samples=np.array(data['optimized_state']),
            energies=np.array([data['final_energy']]),
            metrics={
                'initial_energy': data['initial_energy'],
                'final_energy': data['final_energy'],
                'energy_reduction': data['energy_reduction'],
                'iterations': data['iterations'],
                'converged': data['converged'],
                'method_used': data['method_used']
            },
            metadata={'trajectory': data.get('trajectory')}
        )

    def close(self):
        """Close client session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions
def connect(api_url: str = "http://localhost:8000", api_key: Optional[str] = None) -> IndustriverseClient:
    """
    Connect to Industriverse API.

    Args:
        api_url: Base URL for API
        api_key: Optional API key

    Returns:
        IndustriverseClient instance
    """
    return IndustriverseClient(api_url=api_url, api_key=api_key)
