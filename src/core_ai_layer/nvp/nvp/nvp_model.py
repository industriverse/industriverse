#!/usr/bin/env python3
"""
nvp_model.py
Next Vector Prediction (NVP) Model - Phase 4 Core Component

JAX/Flax implementation of diffusion-based energy state prediction.
Predicts E_{t+1} from E_t with thermodynamic constraints.

Architecture:
    Encoder → Latent Embedding → Decoder → (mean, log_var)

Thermodynamic Principle:
    Predictions must conserve energy and respect entropy bounds.
"""

from typing import Tuple, Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import jax
import jax.numpy as jnp
from jax import random
import flax.linen as nn
from flax.training import train_state
import optax


@dataclass
class NVPConfig:
    """Configuration for NVP model."""
    latent_dim: int = 512
    encoder_features: List[int] = None  # [64, 128, 256]
    decoder_features: List[int] = None  # [256, 128, 64]
    num_scales: int = 3  # Number of pyramid scales
    use_residual: bool = True
    use_batch_norm: bool = True
    dropout_rate: float = 0.1
    activation: str = 'gelu'  # 'gelu', 'relu', 'swish'

    def __post_init__(self):
        if self.encoder_features is None:
            self.encoder_features = [64, 128, 256]
        if self.decoder_features is None:
            self.decoder_features = [256, 128, 64]


class ResidualBlock(nn.Module):
    """Residual block with batch normalization."""
    features: int
    use_batch_norm: bool = True
    dropout_rate: float = 0.1
    activation: Callable = nn.gelu

    @nn.compact
    def __call__(self, x, training: bool = False):
        residual = x

        # First conv
        x = nn.Conv(self.features, kernel_size=(3, 3), padding='SAME')(x)
        if self.use_batch_norm:
            x = nn.BatchNorm(use_running_average=not training)(x)
        x = self.activation(x)
        x = nn.Dropout(self.dropout_rate, deterministic=not training)(x)

        # Second conv
        x = nn.Conv(self.features, kernel_size=(3, 3), padding='SAME')(x)
        if self.use_batch_norm:
            x = nn.BatchNorm(use_running_average=not training)(x)

        # Residual connection (project if needed)
        if residual.shape[-1] != self.features:
            residual = nn.Conv(self.features, kernel_size=(1, 1))(residual)

        x = x + residual
        x = self.activation(x)

        return x


class Encoder(nn.Module):
    """Encoder network: E_t → latent embedding."""
    features: List[int]
    use_residual: bool = True
    use_batch_norm: bool = True
    dropout_rate: float = 0.1
    activation: Callable = nn.gelu

    @nn.compact
    def __call__(self, x, training: bool = False):
        # x shape: (batch, H, W, channels)

        for i, feat in enumerate(self.features):
            # Convolutional layer
            x = nn.Conv(feat, kernel_size=(3, 3), strides=(2, 2), padding='SAME')(x)
            if self.use_batch_norm:
                x = nn.BatchNorm(use_running_average=not training)(x)
            x = self.activation(x)

            # Optional residual block
            if self.use_residual:
                x = ResidualBlock(
                    feat,
                    use_batch_norm=self.use_batch_norm,
                    dropout_rate=self.dropout_rate,
                    activation=self.activation
                )(x, training=training)

        return x


class Decoder(nn.Module):
    """Decoder network: latent → E_{t+1}."""
    features: List[int]
    output_channels: int = 1
    use_residual: bool = True
    use_batch_norm: bool = True
    dropout_rate: float = 0.1
    activation: Callable = nn.gelu

    @nn.compact
    def __call__(self, x, training: bool = False):
        # x shape: (batch, H', W', channels)

        for i, feat in enumerate(self.features):
            # Transposed convolution (upsampling)
            x = nn.ConvTranspose(feat, kernel_size=(3, 3), strides=(2, 2), padding='SAME')(x)
            if self.use_batch_norm:
                x = nn.BatchNorm(use_running_average=not training)(x)
            x = self.activation(x)

            # Optional residual block
            if self.use_residual:
                x = ResidualBlock(
                    feat,
                    use_batch_norm=self.use_batch_norm,
                    dropout_rate=self.dropout_rate,
                    activation=self.activation
                )(x, training=training)

        # Final output layer (no activation for regression)
        x = nn.Conv(self.output_channels, kernel_size=(1, 1))(x)

        return x


class NVPModel(nn.Module):
    """
    Next Vector Prediction (NVP) Model.

    Predicts next energy state E_{t+1} from current state E_t and gradients ∇E_t.
    Outputs both mean and log-variance for Bayesian uncertainty estimation.

    Args:
        config: NVPConfig with model hyperparameters
    """
    config: NVPConfig

    def setup(self):
        # Get activation function
        activation_map = {
            'gelu': nn.gelu,
            'relu': nn.relu,
            'swish': nn.swish
        }
        self.activation = activation_map.get(self.config.activation, nn.gelu)

        # Encoder for energy maps
        self.encoder = Encoder(
            features=self.config.encoder_features,
            use_residual=self.config.use_residual,
            use_batch_norm=self.config.use_batch_norm,
            dropout_rate=self.config.dropout_rate,
            activation=self.activation
        )

        # Encoder for gradients
        self.gradient_encoder = Encoder(
            features=self.config.encoder_features,
            use_residual=self.config.use_residual,
            use_batch_norm=self.config.use_batch_norm,
            dropout_rate=self.config.dropout_rate,
            activation=self.activation
        )

        # Latent fusion layer
        self.latent_fusion = nn.Dense(self.config.latent_dim)

        # Decoders for mean and log-variance
        self.decoder_mean = Decoder(
            features=self.config.decoder_features,
            output_channels=1,
            use_residual=self.config.use_residual,
            use_batch_norm=self.config.use_batch_norm,
            dropout_rate=self.config.dropout_rate,
            activation=self.activation
        )

        self.decoder_logvar = Decoder(
            features=self.config.decoder_features,
            output_channels=1,
            use_residual=self.config.use_residual,
            use_batch_norm=self.config.use_batch_norm,
            dropout_rate=self.config.dropout_rate,
            activation=self.activation
        )

    @nn.compact
    def __call__(
        self,
        energy_t: jnp.ndarray,
        grad_x: jnp.ndarray,
        grad_y: jnp.ndarray,
        training: bool = False
    ) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """
        Forward pass.

        Args:
            energy_t: Current energy map (batch, H, W, 1)
            grad_x: Energy gradient in x direction (batch, H, W, 1)
            grad_y: Energy gradient in y direction (batch, H, W, 1)
            training: Whether in training mode

        Returns:
            mean: Predicted E_{t+1} mean (batch, H, W, 1)
            log_var: Predicted E_{t+1} log-variance (batch, H, W, 1)
        """
        # Encode energy map
        energy_latent = self.encoder(energy_t, training=training)

        # Encode gradients
        gradients = jnp.concatenate([grad_x, grad_y], axis=-1)
        gradient_latent = self.gradient_encoder(gradients, training=training)

        # Fuse latent representations
        # Flatten spatial dimensions
        batch_size = energy_latent.shape[0]
        energy_flat = energy_latent.reshape(batch_size, -1)
        gradient_flat = gradient_latent.reshape(batch_size, -1)

        # Concatenate and fuse
        combined = jnp.concatenate([energy_flat, gradient_flat], axis=-1)
        latent = self.latent_fusion(combined)
        latent = self.activation(latent)
        latent = nn.Dropout(self.config.dropout_rate, deterministic=not training)(latent)

        # Reshape for decoder
        # Compute spatial dimensions after encoding
        H_latent = energy_t.shape[1] // (2 ** len(self.config.encoder_features))
        W_latent = energy_t.shape[2] // (2 ** len(self.config.encoder_features))

        # Project latent to decoder input dimensions
        decoder_channels = self.config.decoder_features[0]
        latent_reshaped = nn.Dense(H_latent * W_latent * decoder_channels)(latent)
        latent_reshaped = latent_reshaped.reshape(
            batch_size, H_latent, W_latent, decoder_channels
        )

        # Decode to mean and log-variance
        mean = self.decoder_mean(latent_reshaped, training=training)
        log_var = self.decoder_logvar(latent_reshaped, training=training)

        # Ensure output has same shape as input
        # If needed, resize using interpolation
        if mean.shape[1:3] != energy_t.shape[1:3]:
            # Use JAX's image resize
            mean = jax.image.resize(
                mean,
                shape=(batch_size, energy_t.shape[1], energy_t.shape[2], 1),
                method='bilinear'
            )
            log_var = jax.image.resize(
                log_var,
                shape=(batch_size, energy_t.shape[1], energy_t.shape[2], 1),
                method='bilinear'
            )

        # Apply softplus to ensure positive energy (energy must be >= 0)
        mean = nn.softplus(mean)

        return mean, log_var

    def predict(
        self,
        energy_t: jnp.ndarray,
        grad_x: jnp.ndarray,
        grad_y: jnp.ndarray,
        rng: Optional[jax.random.PRNGKey] = None
    ) -> jnp.ndarray:
        """
        Predict E_{t+1} with optional stochastic sampling.

        Args:
            energy_t: Current energy map (batch, H, W, 1)
            grad_x: x-gradient (batch, H, W, 1)
            grad_y: y-gradient (batch, H, W, 1)
            rng: Random key for sampling (if None, returns mean)

        Returns:
            Predicted E_{t+1} (batch, H, W, 1)
        """
        mean, log_var = self(energy_t, grad_x, grad_y, training=False)

        if rng is None:
            # Return mean prediction
            return mean
        else:
            # Sample from N(mean, exp(log_var))
            std = jnp.exp(0.5 * log_var)
            epsilon = random.normal(rng, mean.shape)
            return mean + epsilon * std


def create_train_state(
    rng: jax.random.PRNGKey,
    config: NVPConfig,
    learning_rate: float = 1e-4,
    input_shape: Tuple[int, int] = (256, 256)
) -> train_state.TrainState:
    """
    Create initialized training state.

    Args:
        rng: Random key
        config: Model configuration
        learning_rate: Learning rate for Adam optimizer
        input_shape: Spatial dimensions (H, W)

    Returns:
        TrainState with initialized parameters and batch_stats
    """
    # Create model
    model = NVPModel(config)

    # Initialize with dummy inputs
    dummy_energy = jnp.ones((1, input_shape[0], input_shape[1], 1))
    dummy_grad_x = jnp.ones((1, input_shape[0], input_shape[1], 1))
    dummy_grad_y = jnp.ones((1, input_shape[0], input_shape[1], 1))

    # Initialize parameters (returns dict with 'params' and 'batch_stats' if using BatchNorm)
    variables = model.init(
        rng,
        dummy_energy,
        dummy_grad_x,
        dummy_grad_y,
        training=False
    )

    # Create optimizer
    tx = optax.adam(learning_rate)

    # Create train state with batch_stats support
    class TrainStateWithBatchStats(train_state.TrainState):
        batch_stats: Any = None

    state = TrainStateWithBatchStats.create(
        apply_fn=model.apply,
        params=variables['params'],
        tx=tx,
        batch_stats=variables.get('batch_stats')
    )

    return state


def compute_energy_conservation_loss(
    E_pred: jnp.ndarray,
    E_target: jnp.ndarray
) -> jnp.ndarray:
    """
    Compute energy conservation violation.

    L_conservation = |sum(E_pred) - sum(E_target)| / sum(E_target)

    Args:
        E_pred: Predicted energy (batch, H, W, 1)
        E_target: Target energy (batch, H, W, 1)

    Returns:
        Conservation loss (scalar)
    """
    # Sum over spatial dimensions
    E_pred_total = jnp.sum(E_pred, axis=(1, 2, 3))
    E_target_total = jnp.sum(E_target, axis=(1, 2, 3))

    # Relative error
    conservation_error = jnp.abs(E_pred_total - E_target_total) / (E_target_total + 1e-10)

    # Average over batch
    return jnp.mean(conservation_error)


def compute_entropy(E: jnp.ndarray) -> jnp.ndarray:
    """
    Compute Shannon entropy of energy distribution.

    Args:
        E: Energy map (batch, H, W, 1)

    Returns:
        Entropy per sample (batch,)
    """
    # Normalize to probability distribution
    E_normalized = E / (jnp.sum(E, axis=(1, 2, 3), keepdims=True) + 1e-10)

    # Compute entropy: H = -sum(p * log(p))
    entropy = -jnp.sum(
        E_normalized * jnp.log(E_normalized + 1e-10),
        axis=(1, 2, 3)
    )

    return entropy


def compute_entropy_smoothness_loss(
    E_pred: jnp.ndarray,
    E_target: jnp.ndarray,
    threshold: float = 0.1
) -> jnp.ndarray:
    """
    Penalize unphysical entropy decreases.

    L_entropy = max(0, S(E_target) - S(E_pred) - threshold)

    Args:
        E_pred: Predicted energy (batch, H, W, 1)
        E_target: Target energy (batch, H, W, 1)
        threshold: Allowed entropy decrease

    Returns:
        Entropy smoothness loss (scalar)
    """
    S_pred = compute_entropy(E_pred)
    S_target = compute_entropy(E_target)

    # Penalize if S_pred < S_target - threshold
    entropy_violation = jnp.maximum(0.0, S_target - S_pred - threshold)

    # Average over batch
    return jnp.mean(entropy_violation)


# Export public API
__all__ = [
    'NVPModel',
    'NVPConfig',
    'ResidualBlock',
    'Encoder',
    'Decoder',
    'create_train_state',
    'compute_energy_conservation_loss',
    'compute_entropy',
    'compute_entropy_smoothness_loss'
]
