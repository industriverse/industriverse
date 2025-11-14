"""
Diffusion Model Training Pipeline

Main training loop for energy-based diffusion models with thermodynamic
validation and monitoring.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import time
import json
from datetime import datetime
import numpy as np

from ..core.diffusion_dynamics import DiffusionModel, DiffusionConfig
from ..core.energy_field import EnergyField
from ..core.entropy_metrics import EntropyValidator, ThermodynamicMetrics
from .callbacks import TrainingCallback, CallbackList


@dataclass
class TrainingConfig:
    """Configuration for diffusion model training"""

    # Model architecture
    model_channels: int = 128
    num_res_blocks: int = 2
    attention_resolutions: List[int] = field(default_factory=lambda: [16, 8])
    dropout: float = 0.1

    # Training hyperparameters
    num_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    gradient_clip: float = 1.0

    # Diffusion parameters
    timesteps: int = 1000
    noise_schedule: str = "linear"
    beta_start: float = 0.0001
    beta_end: float = 0.02

    # Thermodynamic validation
    energy_tolerance: float = 0.01
    entropy_threshold: float = -1e-6
    validate_every_n_steps: int = 100

    # Checkpointing
    checkpoint_dir: str = "./checkpoints"
    save_every_n_epochs: int = 10
    keep_n_checkpoints: int = 3

    # Logging
    log_every_n_steps: int = 10
    wandb_project: Optional[str] = None
    wandb_entity: Optional[str] = None

    # Device
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    mixed_precision: bool = True


class DiffusionTrainer:
    """
    Training orchestrator for energy-based diffusion models.

    Handles:
    - Forward/reverse diffusion training
    - Thermodynamic validation
    - Checkpointing and logging
    - Callback management
    """

    def __init__(
        self,
        model: DiffusionModel,
        train_dataloader: DataLoader,
        val_dataloader: Optional[DataLoader] = None,
        config: Optional[TrainingConfig] = None,
        callbacks: Optional[List[TrainingCallback]] = None
    ):
        """
        Initialize trainer.

        Args:
            model: Diffusion model to train
            train_dataloader: Training data loader
            val_dataloader: Validation data loader
            config: Training configuration
            callbacks: Training callbacks
        """
        self.model = model
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.config = config or TrainingConfig()

        # Move model to device
        self.device = torch.device(self.config.device)
        self.model.to(self.device)

        # Initialize optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )

        # Learning rate scheduler
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=self.config.num_epochs,
            eta_min=self.config.learning_rate * 0.01
        )

        # Mixed precision scaler
        self.scaler = torch.cuda.amp.GradScaler() if self.config.mixed_precision else None

        # Thermodynamic validator
        self.validator = EntropyValidator(
            energy_tolerance=self.config.energy_tolerance,
            entropy_threshold=self.config.entropy_threshold
        )

        # Energy field for validation
        self.energy_field = EnergyField(
            shape=(64, 64),  # Default, will adapt to input
            temperature=1.0,
            device=self.device
        )

        # Callbacks
        self.callbacks = CallbackList(callbacks or [])

        # Training state
        self.current_epoch = 0
        self.global_step = 0
        self.best_val_loss = float('inf')
        self.metrics_history: List[Dict[str, Any]] = []

        # Setup checkpoint directory
        self.checkpoint_dir = Path(self.config.checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def train(self):
        """Main training loop"""
        self.callbacks.on_train_begin(self)

        for epoch in range(self.config.num_epochs):
            self.current_epoch = epoch

            # Train epoch
            train_metrics = self._train_epoch()

            # Validation
            if self.val_dataloader is not None:
                val_metrics = self._validate_epoch()
            else:
                val_metrics = {}

            # Combine metrics
            epoch_metrics = {
                'epoch': epoch,
                'train': train_metrics,
                'val': val_metrics,
                'lr': self.optimizer.param_groups[0]['lr']
            }
            self.metrics_history.append(epoch_metrics)

            # Callbacks
            self.callbacks.on_epoch_end(epoch, epoch_metrics, self)

            # Checkpointing
            if (epoch + 1) % self.config.save_every_n_epochs == 0:
                self._save_checkpoint(epoch, epoch_metrics)

            # Learning rate schedule
            self.scheduler.step()

            # Log epoch summary
            print(f"\nEpoch {epoch + 1}/{self.config.num_epochs}")
            print(f"  Train Loss: {train_metrics['loss']:.6f}")
            if val_metrics:
                print(f"  Val Loss: {val_metrics['loss']:.6f}")
            print(f"  Energy Fidelity: {train_metrics.get('energy_fidelity', 0.0):.4f}")
            print(f"  Entropy Valid: {train_metrics.get('entropy_valid_rate', 0.0):.2%}")

        self.callbacks.on_train_end(self)

        return self.metrics_history

    def _train_epoch(self) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()

        epoch_losses = []
        epoch_energy_fidelities = []
        epoch_entropy_valid = []

        for batch_idx, batch in enumerate(self.train_dataloader):
            self.callbacks.on_batch_begin(batch_idx, batch, self)

            # Forward pass and compute loss
            loss, metrics = self._training_step(batch)

            # Backward pass
            self.optimizer.zero_grad()

            if self.scaler is not None:
                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip
                )
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip
                )
                self.optimizer.step()

            # Track metrics
            epoch_losses.append(loss.item())
            epoch_energy_fidelities.append(metrics.get('energy_fidelity', 0.0))
            epoch_entropy_valid.append(metrics.get('entropy_valid', 0.0))

            # Callbacks
            batch_metrics = {'loss': loss.item(), **metrics}
            self.callbacks.on_batch_end(batch_idx, batch_metrics, self)

            # Logging
            if (batch_idx + 1) % self.config.log_every_n_steps == 0:
                print(f"  Step {self.global_step}: Loss={loss.item():.6f}, "
                      f"Energy={metrics.get('energy_fidelity', 0.0):.4f}")

            self.global_step += 1

        return {
            'loss': np.mean(epoch_losses),
            'energy_fidelity': np.mean(epoch_energy_fidelities),
            'entropy_valid_rate': np.mean(epoch_entropy_valid)
        }

    def _training_step(self, batch: Dict[str, torch.Tensor]) -> tuple[torch.Tensor, Dict[str, float]]:
        """Single training step"""
        # Get batch data
        x0 = batch['energy_map'].to(self.device)
        batch_size = x0.shape[0]

        # Sample random timesteps
        t = torch.randint(0, self.config.timesteps, (batch_size,), device=self.device)

        # Add noise (forward diffusion)
        noise = torch.randn_like(x0)
        xt = self.model.forward_diffusion.add_noise(x0, t, noise)

        # Predict noise (reverse diffusion)
        if self.config.mixed_precision:
            with torch.cuda.amp.autocast():
                predicted_noise = self.model(xt, t)
                loss = nn.functional.mse_loss(predicted_noise, noise)
        else:
            predicted_noise = self.model(xt, t)
            loss = nn.functional.mse_loss(predicted_noise, noise)

        # Validate thermodynamics (periodically)
        metrics = {}
        if self.global_step % self.config.validate_every_n_steps == 0:
            with torch.no_grad():
                # Reconstruct x0 from prediction
                alpha_t = self.model.forward_diffusion.alphas_cumprod[t]
                x0_pred = (xt - torch.sqrt(1 - alpha_t).view(-1, 1, 1, 1) * predicted_noise) / \
                          torch.sqrt(alpha_t).view(-1, 1, 1, 1)

                # Validate first sample in batch
                thermo_metrics = self.validator.validate_transition(
                    x0[0].squeeze(),
                    x0_pred[0].squeeze()
                )

                metrics['energy_fidelity'] = 1.0 - abs(thermo_metrics.energy_drift)
                metrics['entropy_valid'] = float(thermo_metrics.entropy_monotonic)

        return loss, metrics

    def _validate_epoch(self) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()

        val_losses = []
        val_energy_fidelities = []

        with torch.no_grad():
            for batch in self.val_dataloader:
                x0 = batch['energy_map'].to(self.device)
                batch_size = x0.shape[0]

                # Sample random timesteps
                t = torch.randint(0, self.config.timesteps, (batch_size,), device=self.device)

                # Add noise
                noise = torch.randn_like(x0)
                xt = self.model.forward_diffusion.add_noise(x0, t, noise)

                # Predict
                predicted_noise = self.model(xt, t)
                loss = nn.functional.mse_loss(predicted_noise, noise)

                val_losses.append(loss.item())

                # Energy validation
                alpha_t = self.model.forward_diffusion.alphas_cumprod[t]
                x0_pred = (xt - torch.sqrt(1 - alpha_t).view(-1, 1, 1, 1) * predicted_noise) / \
                          torch.sqrt(alpha_t).view(-1, 1, 1, 1)

                energy_drift = abs(x0.abs().sum() - x0_pred.abs().sum()).item()
                val_energy_fidelities.append(1.0 - energy_drift / (x0.abs().sum().item() + 1e-8))

        return {
            'loss': np.mean(val_losses),
            'energy_fidelity': np.mean(val_energy_fidelities)
        }

    def _save_checkpoint(self, epoch: int, metrics: Dict[str, Any]):
        """Save model checkpoint"""
        checkpoint_path = self.checkpoint_dir / f"checkpoint_epoch_{epoch:04d}.pt"

        checkpoint = {
            'epoch': epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'config': self.config,
            'metrics': metrics,
            'best_val_loss': self.best_val_loss
        }

        if self.scaler is not None:
            checkpoint['scaler_state_dict'] = self.scaler.state_dict()

        torch.save(checkpoint, checkpoint_path)
        print(f"  Checkpoint saved: {checkpoint_path}")

        # Save best model separately
        val_loss = metrics.get('val', {}).get('loss', float('inf'))
        if val_loss < self.best_val_loss:
            self.best_val_loss = val_loss
            best_path = self.checkpoint_dir / "best_model.pt"
            torch.save(checkpoint, best_path)
            print(f"  Best model updated: {best_path}")

        # Clean up old checkpoints
        self._cleanup_checkpoints()

    def _cleanup_checkpoints(self):
        """Remove old checkpoints, keeping only recent N"""
        checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_epoch_*.pt"))

        if len(checkpoints) > self.config.keep_n_checkpoints:
            for checkpoint in checkpoints[:-self.config.keep_n_checkpoints]:
                checkpoint.unlink()

    def load_checkpoint(self, checkpoint_path: str):
        """Load checkpoint and resume training"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        self.current_epoch = checkpoint['epoch']
        self.global_step = checkpoint['global_step']
        self.best_val_loss = checkpoint['best_val_loss']

        if self.scaler is not None and 'scaler_state_dict' in checkpoint:
            self.scaler.load_state_dict(checkpoint['scaler_state_dict'])

        print(f"Checkpoint loaded from {checkpoint_path}")
        print(f"  Epoch: {self.current_epoch}")
        print(f"  Global step: {self.global_step}")
        print(f"  Best val loss: {self.best_val_loss:.6f}")

    def sample(
        self,
        num_samples: int = 16,
        shape: tuple = (1, 64, 64),
        num_inference_steps: int = 50
    ) -> torch.Tensor:
        """
        Generate samples using the trained model.

        Args:
            num_samples: Number of samples to generate
            shape: Shape of each sample
            num_inference_steps: Number of denoising steps

        Returns:
            Generated samples
        """
        self.model.eval()

        with torch.no_grad():
            # Start from noise
            x = torch.randn(num_samples, *shape, device=self.device)

            # Reverse diffusion
            timesteps = torch.linspace(
                self.config.timesteps - 1,
                0,
                num_inference_steps,
                dtype=torch.long,
                device=self.device
            )

            for t in timesteps:
                t_batch = t.repeat(num_samples)

                # Predict noise
                predicted_noise = self.model(x, t_batch)

                # Denoise step
                alpha_t = self.model.forward_diffusion.alphas_cumprod[t]
                alpha_t_prev = self.model.forward_diffusion.alphas_cumprod[max(0, t - 1)]

                # DDPM sampling formula
                pred_x0 = (x - torch.sqrt(1 - alpha_t) * predicted_noise) / torch.sqrt(alpha_t)

                # Clip to valid energy range
                pred_x0 = torch.clamp(pred_x0, -3, 3)

                # Add noise for non-final steps
                if t > 0:
                    noise = torch.randn_like(x)
                    sigma_t = torch.sqrt((1 - alpha_t_prev) / (1 - alpha_t) * (1 - alpha_t / alpha_t_prev))
                    x = torch.sqrt(alpha_t_prev) * pred_x0 + torch.sqrt(1 - alpha_t_prev - sigma_t**2) * predicted_noise + sigma_t * noise
                else:
                    x = pred_x0

        return x
