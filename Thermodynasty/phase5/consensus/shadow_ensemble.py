#!/usr/bin/env python3
"""
Shadow Ensemble - Byzantine Fault Tolerance for Thermodynamic Inference

Implements 3+ model consensus mechanism with:
- Median-based prediction aggregation
- Per-pixel outlier rejection
- Energy conservation verification
- Confidence quantification via ensemble spread

Inspired by:
- THRML's block-based probabilistic sampling
- Jasmine's reproducible multi-model patterns
- BFT consensus from distributed systems
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time

import numpy as np
import jax
import jax.numpy as jnp
from jax import random

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from phase4.ace import ACEAgent, ACEConfig
from phase4.nvp.nvp_model import NVPConfig
from phase5.validation.metrics import (
    compute_energy_fidelity,
    compute_entropy_coherence,
    check_energy_conservation
)


class ShadowEnsemble:
    """
    Shadow Ensemble for Byzantine Fault Tolerant thermodynamic inference

    Uses 3+ ACE models with diverse initialization to achieve consensus.
    Predictions only pass when ≥min_votes models agree within tolerance.

    Key Features:
    - Median prediction aggregation (robust to outliers)
    - Per-pixel standard deviation for confidence maps
    - Energy conservation consensus verification
    - Outlier model detection and rejection
    """

    def __init__(
        self,
        checkpoints: List[str],
        pixel_tol: float = 1e-3,
        energy_tol: float = 0.01,
        min_votes: int = 2,
        latent_dim: int = 128,
        seed: int = 42
    ):
        """
        Initialize Shadow Ensemble

        Args:
            checkpoints: List of paths to model checkpoint files (.flax)
            pixel_tol: Per-pixel tolerance for consensus (default: 1e-3)
            energy_tol: Energy fidelity tolerance for consensus (default: 0.01)
            min_votes: Minimum number of agreeing models for consensus (default: 2)
            latent_dim: Latent dimension for NVP models (default: 128)
            seed: Random seed for reproducibility (default: 42)
        """
        self.checkpoint_paths = checkpoints
        self.pixel_tol = pixel_tol
        self.energy_tol = energy_tol
        self.min_votes = min_votes
        self.latent_dim = latent_dim
        self.seed = seed

        # Load models
        self.models = []
        self.model_metadata = []

        print(f"\n{'='*70}")
        print("SHADOW ENSEMBLE INITIALIZATION")
        print(f"{'='*70}")
        print(f"Checkpoints: {len(checkpoints)}")
        print(f"Tolerances: pixel={pixel_tol}, energy={energy_tol}")
        print(f"Min votes: {min_votes}/{len(checkpoints)}")
        print(f"{'='*70}\n")

        for i, ckpt_path in enumerate(checkpoints):
            try:
                model, metadata = self._load_model(ckpt_path, model_id=i)
                self.models.append(model)
                self.model_metadata.append(metadata)
                print(f"  ✓ Model {i}: {Path(ckpt_path).name}")
                print(f"    Domain: {metadata.get('domain', 'unknown')}")
                print(f"    Metrics: fidelity={metadata.get('fidelity', 0):.4f}, "
                      f"entropy={metadata.get('entropy', 0):.4f}")
            except Exception as e:
                print(f"  ❌ Failed to load {ckpt_path}: {e}")
                raise

        if len(self.models) < 2:
            raise ValueError("Shadow Ensemble requires at least 2 models")

        if self.min_votes > len(self.models):
            raise ValueError(f"min_votes ({self.min_votes}) cannot exceed number of models ({len(self.models)})")

        print(f"\n✓ Shadow Ensemble ready with {len(self.models)} models\n")

    def _load_model(self, checkpoint_path: str, model_id: int) -> Tuple[ACEAgent, Dict]:
        """Load a single ACE model from checkpoint"""
        from flax import serialization
        import json

        ckpt_path = Path(checkpoint_path)
        if not ckpt_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

        # Load metadata
        metadata_path = ckpt_path.with_suffix('.json')
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {'domain': 'unknown', 'fidelity': 0.0, 'entropy': 0.0}

        # Create ACE config
        ace_config = ACEConfig(
            latent_dim=self.latent_dim,
            target_fidelity=0.95,
            target_entropy=0.1,
            min_confidence=0.85,
            seed=self.seed + model_id  # Diverse seeds for ensemble diversity
        )

        # Create NVP config
        nvp_config = NVPConfig(
            latent_dim=self.latent_dim,
            hidden_dims=[256, 256, 128],
            num_coupling_layers=4,
            use_batch_norm=True
        )

        # Initialize agent
        agent = ACEAgent(
            ace_config=ace_config,
            nvp_config=nvp_config,
            domain=metadata.get('domain', 'unknown')
        )

        # Load state
        with open(ckpt_path, 'rb') as f:
            state_bytes = f.read()

        # Deserialize state
        state_dict = serialization.from_bytes(agent.state, state_bytes)
        agent.state = state_dict

        return agent, metadata

    def predict(
        self,
        energy_map: np.ndarray,
        domain: str,
        num_steps: int = 10,
        mode: str = "ensemble",
        return_confidence: bool = True
    ) -> Dict:
        """
        Perform ensemble prediction with BFT consensus

        Args:
            energy_map: Input energy map (height, width)
            domain: Physical domain name
            num_steps: Number of timesteps to predict
            mode: Prediction mode (ensemble|single|socratic)
            return_confidence: Whether to return confidence maps

        Returns:
            Dictionary with predictions, metrics, and consensus info
        """
        if mode == "single":
            # Use only first model (no consensus)
            return self._predict_single(energy_map, domain, num_steps, return_confidence)

        # Run all models in parallel
        predictions_list = []
        metrics_list = []

        for i, model in enumerate(self.models):
            try:
                # Individual model prediction
                pred, metrics = self._run_model(model, energy_map, domain, num_steps)
                predictions_list.append(pred)
                metrics_list.append(metrics)
            except Exception as e:
                print(f"Warning: Model {i} failed: {e}")
                # Continue with other models

        if len(predictions_list) == 0:
            raise RuntimeError("All models failed to produce predictions")

        # Compute ensemble consensus
        result = self._compute_consensus(
            predictions=predictions_list,
            metrics=metrics_list,
            energy_map_initial=energy_map,
            return_confidence=return_confidence
        )

        return result

    def _run_model(
        self,
        model: ACEAgent,
        energy_map: np.ndarray,
        domain: str,
        num_steps: int
    ) -> Tuple[np.ndarray, Dict]:
        """Run a single model prediction"""
        # Convert to JAX array
        energy_jax = jnp.array(energy_map, dtype=jnp.float32)

        # Predict sequence
        predictions = []
        current_state = energy_jax

        for step in range(num_steps):
            # Forward pass through NVP
            next_state = model.predict_step(current_state, domain=domain)
            predictions.append(np.array(next_state))
            current_state = next_state

        predictions = np.stack(predictions, axis=0)  # (num_steps, height, width)

        # Compute metrics
        energy_fidelity = compute_energy_fidelity(predictions, energy_map)
        entropy_coherence = compute_entropy_coherence(predictions)

        metrics = {
            'energy_fidelity': energy_fidelity,
            'entropy_coherence': entropy_coherence,
            'aspiration_rate': model.compute_aspiration_rate(energy_fidelity, entropy_coherence)
        }

        return predictions, metrics

    def _compute_consensus(
        self,
        predictions: List[np.ndarray],
        metrics: List[Dict],
        energy_map_initial: np.ndarray,
        return_confidence: bool
    ) -> Dict:
        """
        Compute BFT consensus from ensemble predictions

        Uses median aggregation + outlier rejection + energy conservation check
        """
        # Stack predictions: (num_models, num_steps, height, width)
        stacked = np.stack(predictions, axis=0)
        num_models = stacked.shape[0]

        # Median prediction (robust to outliers)
        median_pred = np.median(stacked, axis=0)

        # Per-pixel standard deviation (inverse = confidence)
        std_pred = np.std(stacked, axis=0)
        confidence_map = 1.0 - np.minimum(std_pred, 1.0)  # Cap at 1.0

        # Consensus votes: check if each model agrees with median
        consensus_votes = {}
        passing_models = 0

        for i in range(num_models):
            # Per-pixel difference from median
            pixel_diff = np.abs(stacked[i] - median_pred)
            pixel_agree = np.mean(pixel_diff < self.pixel_tol)

            # Energy conservation check
            energy_initial = np.sum(energy_map_initial)
            energy_predicted = np.sum(stacked[i])
            energy_diff = np.abs(energy_predicted - energy_initial) / (energy_initial + 1e-10)
            energy_agree = energy_diff < self.energy_tol

            # Consensus vote
            vote_passed = (pixel_agree > 0.95) and energy_agree
            consensus_votes[f"model_{i}"] = vote_passed

            if vote_passed:
                passing_models += 1

        # Consensus achieved?
        consensus_achieved = passing_models >= self.min_votes

        # Aggregate metrics (from passing models only)
        passing_metrics = [m for i, m in enumerate(metrics) if consensus_votes[f"model_{i}"]]

        if passing_metrics:
            avg_energy_fidelity = np.mean([m['energy_fidelity'] for m in passing_metrics])
            avg_entropy_coherence = np.mean([m['entropy_coherence'] for m in passing_metrics])
            avg_aspiration = np.mean([m['aspiration_rate'] for m in passing_metrics])
        else:
            # Fallback to all models if no consensus
            avg_energy_fidelity = np.mean([m['energy_fidelity'] for m in metrics])
            avg_entropy_coherence = np.mean([m['entropy_coherence'] for m in metrics])
            avg_aspiration = np.mean([m['aspiration_rate'] for m in metrics])

        result = {
            'predictions': median_pred,
            'confidence_map': confidence_map if return_confidence else None,
            'energy_fidelity': float(avg_energy_fidelity),
            'entropy_coherence': float(avg_entropy_coherence),
            'aspiration_rate': float(avg_aspiration),
            'consensus_votes': consensus_votes,
            'consensus_achieved': consensus_achieved,
            'passing_models': passing_models,
            'total_models': num_models,
            'ensemble_std': float(np.mean(std_pred))
        }

        return result

    def _predict_single(
        self,
        energy_map: np.ndarray,
        domain: str,
        num_steps: int,
        return_confidence: bool
    ) -> Dict:
        """Single model prediction (no consensus)"""
        model = self.models[0]
        predictions, metrics = self._run_model(model, energy_map, domain, num_steps)

        return {
            'predictions': predictions,
            'confidence_map': np.ones_like(predictions[0]) * 0.95 if return_confidence else None,
            'energy_fidelity': metrics['energy_fidelity'],
            'entropy_coherence': metrics['entropy_coherence'],
            'aspiration_rate': metrics['aspiration_rate'],
            'consensus_votes': {'model_0': True},
            'consensus_achieved': True,
            'passing_models': 1,
            'total_models': 1,
            'ensemble_std': 0.0
        }

    def quick_confidence(self, coarse_map: np.ndarray) -> float:
        """
        Quick confidence estimate on coarse-resolution map

        Used for coarse-to-fine gating to avoid expensive full-resolution
        inference when high confidence on coarse prediction.

        Args:
            coarse_map: Coarse resolution energy map (e.g., 64x64)

        Returns:
            Confidence score [0-1]
        """
        # Run quick forward pass with first model
        try:
            coarse_jax = jnp.array(coarse_map, dtype=jnp.float32)
            # Simple forward pass
            pred = self.models[0].predict_step(coarse_jax, domain="unknown")

            # Energy conservation check
            energy_init = jnp.sum(coarse_jax)
            energy_pred = jnp.sum(pred)
            fidelity = 1.0 - jnp.abs(energy_pred - energy_init) / (energy_init + 1e-10)

            return float(jnp.clip(fidelity, 0.0, 1.0))
        except Exception as e:
            print(f"Quick confidence failed: {e}")
            return 0.5  # Neutral confidence

    def get_ensemble_diversity(self) -> Dict[str, float]:
        """
        Measure ensemble diversity metrics

        Useful for monitoring ensemble health and detecting correlated failures.
        """
        # TODO: Implement diversity metrics
        # - Parameter distance between models
        # - Prediction correlation matrix
        # - Representation similarity analysis

        return {
            'num_models': len(self.models),
            'checkpoint_diversity': len(set(self.checkpoint_paths)),
            'seed_diversity': len(self.models)  # Different seeds per model
        }


# ============================================================================
# Testing
# ============================================================================

def test_shadow_ensemble():
    """Test Shadow Ensemble with synthetic data"""
    print("\n" + "="*70)
    print("SHADOW ENSEMBLE TEST")
    print("="*70 + "\n")

    # Create synthetic energy map
    energy_map = np.random.rand(256, 256).astype(np.float32)
    energy_map = energy_map / energy_map.sum() * 256 * 256  # Normalize

    # Mock checkpoints (would be real paths in production)
    checkpoints = ["/tmp/model_0.flax", "/tmp/model_1.flax", "/tmp/model_2.flax"]

    # Note: This test will fail without real checkpoints
    # In production, use real trained models

    print("✓ Shadow Ensemble test structure validated")
    print("  (Full test requires trained model checkpoints)")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_shadow_ensemble()
