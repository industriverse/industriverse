"""
Training Callbacks

Callback hooks for monitoring, logging, and controlling the training process.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from pathlib import Path
import json
import time
import numpy as np


class TrainingCallback(ABC):
    """Base class for training callbacks"""

    def on_train_begin(self, trainer):
        """Called at the beginning of training"""
        pass

    def on_train_end(self, trainer):
        """Called at the end of training"""
        pass

    def on_epoch_begin(self, epoch: int, trainer):
        """Called at the beginning of each epoch"""
        pass

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], trainer):
        """Called at the end of each epoch"""
        pass

    def on_batch_begin(self, batch_idx: int, batch: Dict, trainer):
        """Called at the beginning of each batch"""
        pass

    def on_batch_end(self, batch_idx: int, metrics: Dict[str, Any], trainer):
        """Called at the end of each batch"""
        pass


class CallbackList:
    """Container for managing multiple callbacks"""

    def __init__(self, callbacks: List[TrainingCallback]):
        self.callbacks = callbacks

    def on_train_begin(self, trainer):
        for callback in self.callbacks:
            callback.on_train_begin(trainer)

    def on_train_end(self, trainer):
        for callback in self.callbacks:
            callback.on_train_end(trainer)

    def on_epoch_begin(self, epoch: int, trainer):
        for callback in self.callbacks:
            callback.on_epoch_begin(epoch, trainer)

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], trainer):
        for callback in self.callbacks:
            callback.on_epoch_end(epoch, metrics, trainer)

    def on_batch_begin(self, batch_idx: int, batch: Dict, trainer):
        for callback in self.callbacks:
            callback.on_batch_begin(batch_idx, batch, trainer)

    def on_batch_end(self, batch_idx: int, metrics: Dict[str, Any], trainer):
        for callback in self.callbacks:
            callback.on_batch_end(batch_idx, metrics, trainer)


class MetricsLogger(TrainingCallback):
    """
    Logs training metrics to JSON file.
    """

    def __init__(self, log_path: str = "./logs/training_metrics.json"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_history: List[Dict[str, Any]] = []

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], trainer):
        self.metrics_history.append(metrics)

        # Save to file
        with open(self.log_path, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)

    def on_train_end(self, trainer):
        print(f"Training metrics saved to: {self.log_path}")


class ThermodynamicValidator(TrainingCallback):
    """
    Validates thermodynamic properties during training.
    """

    def __init__(
        self,
        validation_frequency: int = 100,
        energy_tolerance: float = 0.01,
        alert_on_violation: bool = True
    ):
        self.validation_frequency = validation_frequency
        self.energy_tolerance = energy_tolerance
        self.alert_on_violation = alert_on_violation
        self.violations: List[Dict[str, Any]] = []

    def on_batch_end(self, batch_idx: int, metrics: Dict[str, Any], trainer):
        if batch_idx % self.validation_frequency == 0:
            # Check energy conservation
            energy_fidelity = metrics.get('energy_fidelity', 1.0)

            if energy_fidelity < (1.0 - self.energy_tolerance):
                violation = {
                    'step': trainer.global_step,
                    'epoch': trainer.current_epoch,
                    'batch': batch_idx,
                    'energy_fidelity': energy_fidelity,
                    'type': 'energy_conservation'
                }
                self.violations.append(violation)

                if self.alert_on_violation:
                    print(f"\n⚠️  Thermodynamic Violation Detected:")
                    print(f"   Step: {trainer.global_step}")
                    print(f"   Energy Fidelity: {energy_fidelity:.4f}")

            # Check entropy monotonicity
            entropy_valid = metrics.get('entropy_valid', 1.0)

            if not entropy_valid:
                violation = {
                    'step': trainer.global_step,
                    'epoch': trainer.current_epoch,
                    'batch': batch_idx,
                    'type': 'entropy_violation'
                }
                self.violations.append(violation)

                if self.alert_on_violation:
                    print(f"\n⚠️  Entropy Violation Detected:")
                    print(f"   Step: {trainer.global_step}")

    def on_train_end(self, trainer):
        if self.violations:
            print(f"\n⚠️  Total Thermodynamic Violations: {len(self.violations)}")
        else:
            print(f"\n✓ No thermodynamic violations detected")


class EarlyStopping(TrainingCallback):
    """
    Early stopping based on validation loss.
    """

    def __init__(
        self,
        patience: int = 10,
        min_delta: float = 1e-4,
        mode: str = 'min'
    ):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode

        self.best_value = float('inf') if mode == 'min' else float('-inf')
        self.counter = 0
        self.should_stop = False

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], trainer):
        val_loss = metrics.get('val', {}).get('loss')

        if val_loss is None:
            return

        # Check improvement
        if self.mode == 'min':
            improved = val_loss < (self.best_value - self.min_delta)
        else:
            improved = val_loss > (self.best_value + self.min_delta)

        if improved:
            self.best_value = val_loss
            self.counter = 0
        else:
            self.counter += 1

        if self.counter >= self.patience:
            print(f"\n⏸️  Early stopping triggered after {epoch + 1} epochs")
            print(f"   Best value: {self.best_value:.6f}")
            self.should_stop = True


class ProgressBar(TrainingCallback):
    """
    Simple text-based progress bar.
    """

    def __init__(self, update_interval: int = 10):
        self.update_interval = update_interval
        self.start_time = None
        self.epoch_start_time = None

    def on_train_begin(self, trainer):
        self.start_time = time.time()
        print("=" * 70)
        print("Training Started")
        print(f"Total Epochs: {trainer.config.num_epochs}")
        print(f"Batch Size: {trainer.config.batch_size}")
        print(f"Learning Rate: {trainer.config.learning_rate}")
        print(f"Device: {trainer.device}")
        print("=" * 70)

    def on_epoch_begin(self, epoch: int, trainer):
        self.epoch_start_time = time.time()
        print(f"\n[Epoch {epoch + 1}/{trainer.config.num_epochs}]")

    def on_batch_end(self, batch_idx: int, metrics: Dict[str, Any], trainer):
        if (batch_idx + 1) % self.update_interval == 0:
            total_batches = len(trainer.train_dataloader)
            progress = (batch_idx + 1) / total_batches * 100

            bar_length = 40
            filled = int(bar_length * (batch_idx + 1) // total_batches)
            bar = '█' * filled + '░' * (bar_length - filled)

            loss = metrics.get('loss', 0.0)
            print(f"\r  {bar} {progress:5.1f}% | Loss: {loss:.6f}", end='', flush=True)

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], trainer):
        epoch_time = time.time() - self.epoch_start_time
        print(f"\n  Epoch Time: {epoch_time:.2f}s")

    def on_train_end(self, trainer):
        total_time = time.time() - self.start_time
        print("\n" + "=" * 70)
        print(f"Training Completed")
        print(f"Total Time: {total_time / 60:.2f} minutes")
        print("=" * 70)


class SampleGenerator(TrainingCallback):
    """
    Generates and saves samples during training.
    """

    def __init__(
        self,
        save_dir: str = "./samples",
        generate_every_n_epochs: int = 10,
        num_samples: int = 16
    ):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.generate_every_n_epochs = generate_every_n_epochs
        self.num_samples = num_samples

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], trainer):
        if (epoch + 1) % self.generate_every_n_epochs == 0:
            print(f"\n  Generating {self.num_samples} samples...")

            # Generate samples
            samples = trainer.sample(
                num_samples=self.num_samples,
                num_inference_steps=50
            )

            # Save samples
            save_path = self.save_dir / f"samples_epoch_{epoch:04d}.npy"
            np.save(save_path, samples.cpu().numpy())

            print(f"  Samples saved: {save_path}")


class GradientMonitor(TrainingCallback):
    """
    Monitors gradient norms to detect training issues.
    """

    def __init__(
        self,
        log_frequency: int = 100,
        gradient_clip_threshold: float = 10.0
    ):
        self.log_frequency = log_frequency
        self.gradient_clip_threshold = gradient_clip_threshold
        self.gradient_norms: List[float] = []

    def on_batch_end(self, batch_idx: int, metrics: Dict[str, Any], trainer):
        if batch_idx % self.log_frequency == 0:
            # Compute total gradient norm
            total_norm = 0.0
            for p in trainer.model.parameters():
                if p.grad is not None:
                    param_norm = p.grad.data.norm(2)
                    total_norm += param_norm.item() ** 2
            total_norm = total_norm ** 0.5

            self.gradient_norms.append(total_norm)

            # Alert if gradient explosion
            if total_norm > self.gradient_clip_threshold:
                print(f"\n⚠️  Large gradient detected: {total_norm:.2f}")

    def on_train_end(self, trainer):
        if self.gradient_norms:
            avg_norm = np.mean(self.gradient_norms)
            max_norm = np.max(self.gradient_norms)
            print(f"\nGradient Statistics:")
            print(f"  Average Norm: {avg_norm:.4f}")
            print(f"  Max Norm: {max_norm:.4f}")


class WandbLogger(TrainingCallback):
    """
    Logs metrics to Weights & Biases.

    Requires: pip install wandb
    """

    def __init__(
        self,
        project: str,
        entity: Optional[str] = None,
        name: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        try:
            import wandb
            self.wandb = wandb
        except ImportError:
            raise ImportError("wandb not installed. Run: pip install wandb")

        self.project = project
        self.entity = entity
        self.name = name
        self.config = config
        self.run = None

    def on_train_begin(self, trainer):
        self.run = self.wandb.init(
            project=self.project,
            entity=self.entity,
            name=self.name,
            config=self.config or trainer.config.__dict__
        )

    def on_batch_end(self, batch_idx: int, metrics: Dict[str, Any], trainer):
        self.wandb.log({
            'batch_loss': metrics.get('loss', 0.0),
            'global_step': trainer.global_step
        })

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], trainer):
        log_dict = {
            'epoch': epoch,
            'train_loss': metrics.get('train', {}).get('loss', 0.0),
            'val_loss': metrics.get('val', {}).get('loss', 0.0),
            'energy_fidelity': metrics.get('train', {}).get('energy_fidelity', 0.0),
            'learning_rate': metrics.get('lr', 0.0)
        }
        self.wandb.log(log_dict)

    def on_train_end(self, trainer):
        if self.run is not None:
            self.run.finish()


class LearningRateScheduler(TrainingCallback):
    """
    Custom learning rate scheduling.
    """

    def __init__(
        self,
        schedule_type: str = 'step',
        step_size: int = 30,
        gamma: float = 0.1,
        warmup_epochs: int = 0
    ):
        self.schedule_type = schedule_type
        self.step_size = step_size
        self.gamma = gamma
        self.warmup_epochs = warmup_epochs
        self.base_lr = None

    def on_train_begin(self, trainer):
        self.base_lr = trainer.config.learning_rate

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], trainer):
        # Warmup phase
        if epoch < self.warmup_epochs:
            lr = self.base_lr * (epoch + 1) / self.warmup_epochs
            for param_group in trainer.optimizer.param_groups:
                param_group['lr'] = lr
            return

        # Main schedule
        if self.schedule_type == 'step':
            if (epoch + 1) % self.step_size == 0:
                for param_group in trainer.optimizer.param_groups:
                    param_group['lr'] *= self.gamma

        elif self.schedule_type == 'cosine':
            lr = self.base_lr * 0.5 * (1 + np.cos(np.pi * epoch / trainer.config.num_epochs))
            for param_group in trainer.optimizer.param_groups:
                param_group['lr'] = lr
