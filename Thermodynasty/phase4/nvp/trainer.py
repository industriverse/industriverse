#!/usr/bin/env python3
"""
trainer.py
NVP Model Training Loop - Phase 4 Core Component

Implements thermodynamic loss function and training loop.

Loss Function:
    L_total = L_MSE + λ₁ * L_conservation + λ₂ * L_entropy

Thermodynamic Constraints:
    - Energy conservation: ∑E_pred ≈ ∑E_target
    - Entropy smoothness: S(E_{t+1}) ≥ S(E_t) - threshold
"""

from typing import Dict, Tuple, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import time
from datetime import datetime

import numpy as np
import jax
import jax.numpy as jnp
from jax import random
from flax.training import train_state, checkpoints
from flax import serialization
import optax

from .nvp_model import (
    NVPModel,
    NVPConfig,
    create_train_state,
    compute_energy_conservation_loss,
    compute_entropy_smoothness_loss
)


@dataclass
class TrainingConfig:
    """Configuration for NVP training."""
    # Model config
    model_config: NVPConfig = None

    # Training hyperparameters
    batch_size: int = 16
    num_epochs: int = 100
    learning_rate: float = 1e-4
    val_split: float = 0.05  # 5% for validation

    # Loss weights
    lambda_conservation: float = 0.1  # λ₁
    lambda_entropy: float = 0.05  # λ₂
    entropy_threshold: float = 0.1  # Allowed entropy decrease

    # Checkpointing
    checkpoint_dir: str = "phase4/checkpoints"
    checkpoint_every: int = 10  # Save every N epochs
    keep_last_n: int = 5  # Keep last N checkpoints

    # Logging
    log_every: int = 10  # Log every N steps
    log_dir: str = "phase4/logs"

    # Data
    input_shape: Tuple[int, int] = (256, 256)

    # Random seed
    seed: int = 42

    def __post_init__(self):
        if self.model_config is None:
            self.model_config = NVPConfig()


@dataclass
class TrainingMetrics:
    """Metrics tracked during training."""
    epoch: int
    step: int
    loss_total: float
    loss_mse: float
    loss_conservation: float
    loss_entropy: float
    energy_fidelity: float
    rmse: float
    entropy_coherence: float
    time_elapsed: float


class Trainer:
    """NVP model trainer with thermodynamic constraints."""

    def __init__(self, config: TrainingConfig):
        self.config = config

        # Create directories
        Path(config.checkpoint_dir).mkdir(parents=True, exist_ok=True)
        Path(config.log_dir).mkdir(parents=True, exist_ok=True)

        # Initialize RNG
        self.rng = random.PRNGKey(config.seed)

        # Initialize training state (will be set in train())
        self.state = None

        # Metrics history
        self.train_metrics: List[TrainingMetrics] = []
        self.val_metrics: List[TrainingMetrics] = []

    def compute_loss(
        self,
        params: Any,
        batch: Dict[str, jnp.ndarray],
        training: bool = True
    ) -> Tuple[jnp.ndarray, Dict[str, jnp.ndarray]]:
        """
        Compute thermodynamic loss function.

        L_total = L_MSE + λ₁ * L_conservation + λ₂ * L_entropy

        Args:
            params: Model parameters
            batch: Dictionary with 'energy_t', 'grad_x', 'grad_y', 'energy_target'
            training: Whether in training mode

        Returns:
            loss: Total loss (scalar)
            metrics: Dictionary of individual loss components
        """
        # Forward pass
        mean_pred, log_var_pred = self.state.apply_fn(
            params,
            batch['energy_t'],
            batch['grad_x'],
            batch['grad_y'],
            training=training
        )

        # MSE loss (reconstruction)
        mse_loss = jnp.mean((mean_pred - batch['energy_target']) ** 2)

        # Energy conservation loss
        conservation_loss = compute_energy_conservation_loss(
            mean_pred,
            batch['energy_target']
        )

        # Entropy smoothness loss
        entropy_loss = compute_entropy_smoothness_loss(
            mean_pred,
            batch['energy_target'],
            threshold=self.config.entropy_threshold
        )

        # Total loss
        total_loss = (
            mse_loss +
            self.config.lambda_conservation * conservation_loss +
            self.config.lambda_entropy * entropy_loss
        )

        # Compute additional metrics
        # Energy fidelity: 1 - |ΔE| / |E|
        delta_E = jnp.abs(
            jnp.sum(mean_pred, axis=(1, 2, 3)) -
            jnp.sum(batch['energy_target'], axis=(1, 2, 3))
        )
        total_E = jnp.sum(batch['energy_target'], axis=(1, 2, 3))
        fidelity = 1.0 - jnp.mean(delta_E / (total_E + 1e-10))

        # RMSE
        rmse = jnp.sqrt(mse_loss)

        # Entropy coherence
        from .nvp_model import compute_entropy
        S_pred = compute_entropy(mean_pred)
        S_target = compute_entropy(batch['energy_target'])
        entropy_coherence = 1.0 - jnp.mean(
            jnp.abs(S_pred - S_target) / (S_target + 1e-10)
        )

        metrics = {
            'loss_total': total_loss,
            'loss_mse': mse_loss,
            'loss_conservation': conservation_loss,
            'loss_entropy': entropy_loss,
            'energy_fidelity': fidelity,
            'rmse': rmse,
            'entropy_coherence': entropy_coherence
        }

        return total_loss, metrics

    def train_step(
        self,
        state: train_state.TrainState,
        batch: Dict[str, jnp.ndarray]
    ) -> Tuple[train_state.TrainState, Dict[str, jnp.ndarray]]:
        """
        Single training step.

        Args:
            state: Training state
            batch: Input batch

        Returns:
            Updated state and metrics
        """
        def loss_fn(params):
            return self.compute_loss(params, batch, training=True)

        # Compute gradients
        (loss, metrics), grads = jax.value_and_grad(loss_fn, has_aux=True)(state.params)

        # Update parameters
        state = state.apply_gradients(grads=grads)

        return state, metrics

    def val_step(
        self,
        state: train_state.TrainState,
        batch: Dict[str, jnp.ndarray]
    ) -> Dict[str, jnp.ndarray]:
        """
        Single validation step.

        Args:
            state: Training state
            batch: Input batch

        Returns:
            Metrics dictionary
        """
        _, metrics = self.compute_loss(state.params, batch, training=False)
        return metrics

    def prepare_batch(
        self,
        energy_sequence: np.ndarray,
        gradients: np.ndarray,
        indices: np.ndarray
    ) -> Dict[str, jnp.ndarray]:
        """
        Prepare batch for training.

        Args:
            energy_sequence: Temporal sequence (N, T, H, W)
            gradients: Precomputed gradients (N, T, H, W, 2)
            indices: Batch indices

        Returns:
            Batch dictionary
        """
        batch_energy = energy_sequence[indices]
        batch_gradients = gradients[indices]

        # Extract E_t and E_{t+1}
        energy_t = batch_energy[:, :-1]  # (batch, T-1, H, W)
        energy_target = batch_energy[:, 1:]  # (batch, T-1, H, W)

        # Flatten temporal dimension
        batch_size, T_minus_1, H, W = energy_t.shape
        energy_t = energy_t.reshape(-1, H, W, 1)
        energy_target = energy_target.reshape(-1, H, W, 1)

        # Gradients
        grad_x = batch_gradients[:, :-1, :, :, 0].reshape(-1, H, W, 1)
        grad_y = batch_gradients[:, :-1, :, :, 1].reshape(-1, H, W, 1)

        return {
            'energy_t': jnp.array(energy_t),
            'grad_x': jnp.array(grad_x),
            'grad_y': jnp.array(grad_y),
            'energy_target': jnp.array(energy_target)
        }

    def train(
        self,
        train_data: Dict[str, np.ndarray],
        val_data: Optional[Dict[str, np.ndarray]] = None,
        verbose: bool = True
    ) -> Dict[str, List[TrainingMetrics]]:
        """
        Train NVP model.

        Args:
            train_data: Dictionary with 'energy_sequence' (N, T, H, W) and 'gradients' (N, T, H, W, 2)
            val_data: Optional validation data
            verbose: Whether to print progress

        Returns:
            Training history
        """
        # Initialize model
        self.rng, init_rng = random.split(self.rng)
        self.state = create_train_state(
            init_rng,
            self.config.model_config,
            learning_rate=self.config.learning_rate,
            input_shape=self.config.input_shape
        )

        # Extract data
        energy_sequence = train_data['energy_sequence']
        gradients = train_data['gradients']
        N = energy_sequence.shape[0]

        # Validation data
        if val_data is not None:
            val_energy = val_data['energy_sequence']
            val_gradients = val_data['gradients']
            N_val = val_energy.shape[0]

        # Training loop
        start_time = time.time()
        global_step = 0

        for epoch in range(self.config.num_epochs):
            epoch_start = time.time()

            # Shuffle training data
            self.rng, shuffle_rng = random.split(self.rng)
            perm = random.permutation(shuffle_rng, N)

            # Training
            epoch_metrics = []
            num_batches = N // self.config.batch_size

            for batch_idx in range(num_batches):
                # Get batch indices
                batch_start = batch_idx * self.config.batch_size
                batch_end = batch_start + self.config.batch_size
                batch_indices = perm[batch_start:batch_end]

                # Prepare batch
                batch = self.prepare_batch(energy_sequence, gradients, batch_indices)

                # Training step
                self.state, metrics = self.train_step(self.state, batch)

                # Convert metrics to numpy
                metrics = {k: float(v) for k, v in metrics.items()}
                epoch_metrics.append(metrics)

                global_step += 1

                # Logging
                if verbose and global_step % self.config.log_every == 0:
                    print(
                        f"Epoch {epoch+1}/{self.config.num_epochs}, "
                        f"Step {global_step}, "
                        f"Loss: {metrics['loss_total']:.4f}, "
                        f"Fidelity: {metrics['energy_fidelity']:.4f}"
                    )

            # Average epoch metrics
            avg_metrics = {
                k: np.mean([m[k] for m in epoch_metrics])
                for k in epoch_metrics[0].keys()
            }

            # Store training metrics
            self.train_metrics.append(TrainingMetrics(
                epoch=epoch,
                step=global_step,
                time_elapsed=time.time() - start_time,
                **avg_metrics
            ))

            # Validation
            if val_data is not None:
                val_metrics_list = []
                num_val_batches = N_val // self.config.batch_size

                for batch_idx in range(num_val_batches):
                    batch_start = batch_idx * self.config.batch_size
                    batch_end = batch_start + self.config.batch_size
                    val_indices = np.arange(batch_start, batch_end)

                    batch = self.prepare_batch(val_energy, val_gradients, val_indices)
                    val_metrics = self.val_step(self.state, batch)

                    val_metrics = {k: float(v) for k, v in val_metrics.items()}
                    val_metrics_list.append(val_metrics)

                # Average validation metrics
                avg_val_metrics = {
                    k: np.mean([m[k] for m in val_metrics_list])
                    for k in val_metrics_list[0].keys()
                }

                self.val_metrics.append(TrainingMetrics(
                    epoch=epoch,
                    step=global_step,
                    time_elapsed=time.time() - start_time,
                    **avg_val_metrics
                ))

                if verbose:
                    print(
                        f"  Val - Loss: {avg_val_metrics['loss_total']:.4f}, "
                        f"Fidelity: {avg_val_metrics['energy_fidelity']:.4f}"
                    )

            # Checkpointing
            if (epoch + 1) % self.config.checkpoint_every == 0:
                self.save_checkpoint(epoch)

            if verbose:
                epoch_time = time.time() - epoch_start
                print(f"  Epoch time: {epoch_time:.2f}s\n")

        # Save final checkpoint
        self.save_checkpoint(self.config.num_epochs - 1, final=True)

        # Save training history
        self.save_metrics()

        return {
            'train': self.train_metrics,
            'val': self.val_metrics
        }

    def save_checkpoint(self, epoch: int, final: bool = False):
        """Save model checkpoint."""
        checkpoint_dir = Path(self.config.checkpoint_dir)

        if final:
            checkpoint_name = "final"
        else:
            checkpoint_name = f"epoch_{epoch+1:04d}"

        checkpoints.save_checkpoint(
            ckpt_dir=str(checkpoint_dir),
            target=self.state,
            step=epoch,
            prefix=checkpoint_name,
            keep=self.config.keep_last_n if not final else None
        )

        print(f"  Saved checkpoint: {checkpoint_name}")

    def load_checkpoint(self, checkpoint_path: str):
        """Load model from checkpoint."""
        self.state = checkpoints.restore_checkpoint(
            ckpt_dir=checkpoint_path,
            target=self.state
        )

        print(f"Loaded checkpoint from: {checkpoint_path}")

    def save_metrics(self):
        """Save training metrics to JSON."""
        log_dir = Path(self.config.log_dir)

        # Convert metrics to dict
        train_metrics_dict = [asdict(m) for m in self.train_metrics]
        val_metrics_dict = [asdict(m) for m in self.val_metrics]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(log_dir / f"train_metrics_{timestamp}.json", 'w') as f:
            json.dump(train_metrics_dict, f, indent=2)

        if val_metrics_dict:
            with open(log_dir / f"val_metrics_{timestamp}.json", 'w') as f:
                json.dump(val_metrics_dict, f, indent=2)

        print(f"Saved metrics to: {log_dir}")


def prepare_training_data(
    energy_sequences: List[np.ndarray],
    atlas_loader
) -> Dict[str, np.ndarray]:
    """
    Prepare training data from energy sequences.

    Args:
        energy_sequences: List of sequences (each T x H x W)
        atlas_loader: EnergyAtlasLoader instance for gradient computation

    Returns:
        Dictionary with 'energy_sequence' and 'gradients'
    """
    all_sequences = []
    all_gradients = []

    for seq in energy_sequences:
        T, H, W = seq.shape

        # Compute gradients for each timestep
        seq_gradients = []
        for t in range(T):
            grad_x, grad_y = atlas_loader.compute_gradients(seq[t])
            seq_gradients.append(np.stack([grad_x, grad_y], axis=-1))

        all_sequences.append(seq)
        all_gradients.append(np.stack(seq_gradients, axis=0))

    return {
        'energy_sequence': np.stack(all_sequences, axis=0),
        'gradients': np.stack(all_gradients, axis=0)
    }


# Export public API
__all__ = [
    'Trainer',
    'TrainingConfig',
    'TrainingMetrics',
    'prepare_training_data'
]
