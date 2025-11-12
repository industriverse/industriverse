#!/usr/bin/env python3
"""
train_ace.py
Production Training Script with ACE Agent Integration

Enhanced training with:
- ACE cognitive architecture
- Socratic self-correction
- Shadow ensemble (optional)
- Real-time confidence monitoring
- Adaptive goal adjustment
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import jax
import jax.numpy as jnp
from jax import random
import time
from typing import Dict, List
import pickle
import json
from flax import serialization

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase4.core.atlas_loader import EnergyAtlasLoader
from phase4.ace import (
    ACEAgent,
    ACEConfig,
    AspirationConfig,
    CalibrationConfig,
    ExecutionConfig,
    SocraticACEAgent,
    SocraticConfig,
    EnsembleACEAgent,
    EnsembleConfig
)
from phase4.nvp.nvp_model import NVPConfig
from phase4.nvp.trainer import Trainer, TrainingConfig, prepare_training_data


def load_domain_sequences(
    domain: str,
    data_dir: Path,
    max_sequences: int = 10
) -> tuple:
    """Load energy map sequences for a domain.

    Returns:
        tuple: (sequences, loader) where sequences is a list of arrays
               and loader is the EnergyAtlasLoader instance
    """
    loader = EnergyAtlasLoader(data_dir, neo4j_uri=None)

    domain_dir = data_dir / "energy_maps" / domain
    if not domain_dir.exists():
        raise FileNotFoundError(f"Domain directory not found: {domain_dir}")

    # Get all map files
    map_files = sorted(domain_dir.glob("*.npy"))

    if len(map_files) == 0:
        raise ValueError(f"No maps found for domain: {domain}")

    # Group into sequences of 10 timesteps
    sequences = []
    sequence_length = 10

    for i in range(0, len(map_files), sequence_length):
        if max_sequences and len(sequences) >= max_sequences:
            break

        seq_files = map_files[i:i+sequence_length]
        if len(seq_files) < sequence_length:
            break

        # Load sequence
        sequence = []
        for f in seq_files:
            energy_map = np.load(f)
            sequence.append(energy_map)

        sequences.append(np.stack(sequence, axis=0))

    return sequences, loader


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Train NVP model with ACE cognitive architecture'
    )

    # Data
    parser.add_argument('--domain', type=str, default='plasma_physics',
                       help='Domain to train on')
    parser.add_argument('--data-path', type=str, default=None,
                       help='Path to energy atlas data')
    parser.add_argument('--max-sequences', type=int, default=None,
                       help='Maximum sequences to load')

    # Training
    parser.add_argument('--epochs', type=int, default=10,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=8,
                       help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=1e-4,
                       help='Learning rate')

    # ACE Configuration
    parser.add_argument('--use-ace', action='store_true',
                       help='Use ACE agent for enhanced training')
    parser.add_argument('--use-socratic', action='store_true',
                       help='Use Socratic self-correction')
    parser.add_argument('--use-ensemble', action='store_true',
                       help='Use shadow ensemble (3 models)')

    # ACE Goals
    parser.add_argument('--target-fidelity', type=float, default=0.90,
                       help='Target energy fidelity')
    parser.add_argument('--target-entropy', type=float, default=0.85,
                       help='Target entropy coherence')
    parser.add_argument('--min-confidence', type=float, default=0.70,
                       help='Minimum prediction confidence')

    # Socratic
    parser.add_argument('--socratic-iterations', type=int, default=3,
                       help='Max Socratic correction iterations')

    # Model
    parser.add_argument('--latent-dim', type=int, default=128,
                       help='Latent dimension')
    parser.add_argument('--checkpoint-path', type=str, default=None,
                       help='Path to model checkpoint to load')
    parser.add_argument('--checkpoint-dir', type=str, default='checkpoints',
                       help='Directory to save checkpoints')

    # Logging
    parser.add_argument('--log-dir', type=str, default='logs',
                       help='Directory for logs')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    return parser.parse_args()


def create_ace_agent(
    args,
    input_shape: tuple,
    checkpoint_path: Path = None
) -> ACEAgent:
    """
    Create ACE agent based on configuration.

    Args:
        args: Command-line arguments
        input_shape: Input shape (H, W)
        checkpoint_path: Optional checkpoint path

    Returns:
        Configured ACE agent (ACE, Socratic, or Ensemble)
    """
    # Base NVP config
    nvp_config = NVPConfig(
        latent_dim=args.latent_dim,
        encoder_features=[64, 128, 256],
        decoder_features=[256, 128, 64],
        num_scales=3
    )

    # ACE configuration
    ace_config = ACEConfig(
        aspiration=AspirationConfig(
            target_energy_fidelity=args.target_fidelity,
            target_entropy_coherence=args.target_entropy,
            min_confidence=args.min_confidence
        ),
        calibration=CalibrationConfig(
            num_samples=10,
            confidence_method="entropy",
            use_ensemble=args.use_ensemble,
            ensemble_size=3 if args.use_ensemble else 1
        ),
        execution=ExecutionConfig(
            nvp_config=nvp_config,
            input_shape=input_shape,
            enforce_energy_conservation=True,
            enforce_entropy_monotonicity=True
        )
    )

    # Create agent based on configuration
    if args.use_ensemble:
        ensemble_config = EnsembleConfig(
            num_models=3,
            consensus_method="median",
            max_disagreement=0.2
        )

        if args.use_socratic:
            # Ensemble + Socratic (full stack)
            base_agent = EnsembleACEAgent(
                ace_config,
                ensemble_config,
                model_paths=None  # Will train from scratch
            )

            socratic_config = SocraticConfig(
                max_iterations=args.socratic_iterations,
                verbose=args.verbose
            )

            # Wrap ensemble in Socratic loop (functional approach)
            return base_agent, socratic_config
        else:
            # Ensemble only
            return EnsembleACEAgent(
                ace_config,
                ensemble_config,
                model_paths=None
            ), None

    elif args.use_socratic:
        # Socratic + single model
        socratic_config = SocraticConfig(
            max_iterations=args.socratic_iterations,
            verbose=args.verbose
        )

        return SocraticACEAgent(
            ace_config,
            socratic_config,
            model_path=checkpoint_path
        ), None

    else:
        # Basic ACE agent
        return ACEAgent(ace_config, model_path=checkpoint_path), None


def train_with_ace(
    args,
    agent: ACEAgent,
    socratic_config,
    train_data: Dict,
    val_data: Dict = None
):
    """
    Train using ACE agent with optional Socratic correction.

    Args:
        args: Command-line arguments
        agent: ACE agent
        socratic_config: Socratic configuration (if enabled)
        train_data: Training data
        val_data: Validation data (optional)
    """
    print("\n" + "="*60)
    print("ACE-ENHANCED TRAINING")
    print("="*60)
    print(f"Agent Type: {type(agent).__name__}")
    print(f"Socratic Correction: {socratic_config is not None}")
    print(f"Shadow Ensemble: {hasattr(agent, 'ensemble')}")
    print(f"Target Fidelity: {args.target_fidelity}")
    print(f"Target Entropy: {args.target_entropy}")
    print(f"Min Confidence: {args.min_confidence}")
    print("="*60)

    # Extract training data
    energy_seq = train_data['energy_sequence']
    gradients = train_data['gradients']
    N, T, H, W = energy_seq.shape

    print(f"\nTraining Data:")
    print(f"  Sequences: {N}")
    print(f"  Timesteps: {T}")
    print(f"  Resolution: {H}×{W}")

    # Training loop
    epoch_history = []

    for epoch in range(args.epochs):
        epoch_start = time.time()
        print(f"\nEpoch {epoch + 1}/{args.epochs}")
        print("-" * 60)

        epoch_metrics = {
            'confidence': [],
            'energy_fidelity': [],
            'entropy_coherence': [],
            'aspiration_met': [],
            'num_retries': []
        }

        # Iterate through sequences
        for seq_idx in range(N):
            # Get sequence
            seq_energy = energy_seq[seq_idx]
            seq_grads = gradients[seq_idx]

            # Predict each timestep
            for t in range(T - 1):
                energy_t = seq_energy[t]
                energy_target = seq_energy[t + 1]
                grad_x = seq_grads[t, :, :, 0]
                grad_y = seq_grads[t, :, :, 1]

                # Make prediction (with Socratic if enabled)
                if socratic_config is not None:
                    from phase4.ace import SocraticLoop
                    loop = SocraticLoop(socratic_config)
                    result, history = loop.predict_with_correction(
                        agent, energy_t, grad_x, grad_y, energy_target
                    )
                else:
                    result = agent.predict(energy_t, grad_x, grad_y, energy_target)

                # Track metrics
                epoch_metrics['confidence'].append(result.confidence)
                epoch_metrics['energy_fidelity'].append(result.energy_fidelity)
                epoch_metrics['entropy_coherence'].append(result.entropy_coherence)
                epoch_metrics['aspiration_met'].append(result.aspiration_met)
                epoch_metrics['num_retries'].append(result.num_retries)

        # Compute epoch statistics
        epoch_stats = {
            'epoch': epoch + 1,
            'mean_confidence': float(np.mean(epoch_metrics['confidence'])),
            'mean_fidelity': float(np.mean(epoch_metrics['energy_fidelity'])),
            'mean_entropy': float(np.mean(epoch_metrics['entropy_coherence'])),
            'aspiration_rate': float(np.mean(epoch_metrics['aspiration_met'])),
            'mean_retries': float(np.mean(epoch_metrics['num_retries'])),
            'time': time.time() - epoch_start
        }

        epoch_history.append(epoch_stats)

        # Print epoch summary
        print(f"\nEpoch {epoch + 1} Summary:")
        print(f"  Confidence:       {epoch_stats['mean_confidence']:.4f}")
        print(f"  Energy Fidelity:  {epoch_stats['mean_fidelity']:.4f}")
        print(f"  Entropy Coherence: {epoch_stats['mean_entropy']:.4f}")
        print(f"  Aspiration Rate:  {epoch_stats['aspiration_rate']:.2%}")
        if socratic_config:
            print(f"  Avg Retries:      {epoch_stats['mean_retries']:.2f}")
        print(f"  Time: {epoch_stats['time']:.2f}s")

    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)

    # Final statistics
    final_stats = epoch_history[-1]
    print(f"\nFinal Metrics:")
    print(f"  Confidence:       {final_stats['mean_confidence']:.4f}")
    print(f"  Energy Fidelity:  {final_stats['mean_fidelity']:.4f}")
    print(f"  Entropy Coherence: {final_stats['mean_entropy']:.4f}")
    print(f"  Aspiration Rate:  {final_stats['aspiration_rate']:.2%}")

    # Check if goals achieved
    goals_met = (
        final_stats['mean_fidelity'] >= args.target_fidelity and
        final_stats['mean_entropy'] >= args.target_entropy and
        final_stats['mean_confidence'] >= args.min_confidence
    )

    if goals_met:
        print("\n✓ ALL GOALS ACHIEVED!")
    else:
        print("\n⚠ Some goals not met:")
        if final_stats['mean_fidelity'] < args.target_fidelity:
            print(f"  Energy Fidelity: {final_stats['mean_fidelity']:.4f} < {args.target_fidelity}")
        if final_stats['mean_entropy'] < args.target_entropy:
            print(f"  Entropy Coherence: {final_stats['mean_entropy']:.4f} < {args.target_entropy}")
        if final_stats['mean_confidence'] < args.min_confidence:
            print(f"  Confidence: {final_stats['mean_confidence']:.4f} < {args.min_confidence}")

    return epoch_history


def save_checkpoint(
    agent,
    args,
    final_metrics: Dict,
    checkpoint_dir: Path
) -> Path:
    """
    Save trained ACE agent checkpoint.

    Args:
        agent: Trained ACE agent
        args: Training arguments
        final_metrics: Final training metrics
        checkpoint_dir: Directory to save checkpoint

    Returns:
        Path to saved checkpoint
    """
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Create checkpoint name
    agent_type = type(agent).__name__
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    checkpoint_name = f"{agent_type}_{args.domain}_ep{args.epochs}_{timestamp}"

    # Handle different agent types
    if hasattr(agent, 'ensemble'):
        # EnsembleACEAgent - has ensemble instead of execution
        print(f"\nSaving Ensemble Agent ({agent.ensemble.config.num_models} models)...")

        for i, model in enumerate(agent.ensemble.models):
            # Each model in ensemble is an ExecutionLayer with state
            state = model.state
            state_dict = {
                'params': state.params,
                'step': int(state.step),
            }
            if hasattr(state, 'batch_stats'):
                state_dict['batch_stats'] = state.batch_stats

            # Serialize
            state_bytes = serialization.to_bytes(state_dict)

            # Save ensemble model state
            model_path = checkpoint_dir / f"{checkpoint_name}_ensemble{i}_state.flax"
            with open(model_path, 'wb') as f:
                f.write(model_bytes)

            print(f"  ✓ Saved model {i+1}/{agent.ensemble.config.num_models}")

        # Use first model's config for metadata
        input_shape = list(agent.ensemble.models[0].config.input_shape)
        state_path = checkpoint_dir / f"{checkpoint_name}_ensemble0_state.flax"

    elif hasattr(agent, 'execution'):
        # Regular ACEAgent or SocraticACEAgent
        execution_layer = agent.execution
        input_shape = list(execution_layer.config.input_shape)

        # Extract serializable state components
        state = execution_layer.state
        state_dict = {
            'params': state.params,
            'step': int(state.step),
        }

        # Add batch_stats if present
        if hasattr(state, 'batch_stats'):
            state_dict['batch_stats'] = state.batch_stats

        # Serialize JAX arrays using Flax serialization
        state_bytes = serialization.to_bytes(state_dict)

        # Save model state (JAX arrays as bytes)
        state_path = checkpoint_dir / f"{checkpoint_name}_state.flax"
        with open(state_path, 'wb') as f:
            f.write(state_bytes)

    else:
        raise AttributeError("Cannot find execution layer or ensemble in agent")

    # Prepare metadata (pickleable config info)
    metadata = {
        'agent_type': agent_type,
        'domain': args.domain,
        'epochs': args.epochs,
        'latent_dim': args.latent_dim,
        'input_shape': input_shape,
        'target_fidelity': args.target_fidelity,
        'target_entropy': args.target_entropy,
        'min_confidence': args.min_confidence,
        'final_metrics': final_metrics,
        'timestamp': timestamp
    }

    # Add ensemble info if applicable
    if hasattr(agent, 'ensemble'):
        metadata['num_ensemble_models'] = agent.ensemble.config.num_models

    # Save metadata as JSON
    metadata_path = checkpoint_dir / f"{checkpoint_name}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Checkpoint saved:")
    print(f"  State: {state_path}")
    print(f"  Metadata: {metadata_path}")

    return state_path


def main():
    """Main training script."""
    args = parse_args()

    print("="*60)
    print("NVP TRAINING WITH ACE COGNITIVE ARCHITECTURE")
    print("="*60)
    print(f"Domain: {args.domain}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Learning Rate: {args.learning_rate}")
    print(f"ACE Enhanced: {args.use_ace}")
    print(f"Socratic Correction: {args.use_socratic}")
    print(f"Shadow Ensemble: {args.use_ensemble}")

    # Load data
    print("\nLoading energy map sequences...")
    data_dir = Path(args.data_path) if args.data_path else Path.cwd() / "data"

    # Load sequences for domain
    sequences, loader = load_domain_sequences(
        domain=args.domain,
        data_dir=data_dir,
        max_sequences=args.max_sequences if args.max_sequences else 10
    )

    print(f"Loaded {len(sequences)} sequences")

    if len(sequences) == 0:
        print("ERROR: No sequences loaded!")
        return

    # Prepare training data
    print("Preparing training data (computing gradients)...")
    train_data = prepare_training_data(sequences, loader)

    energy_shape = train_data['energy_sequence'].shape
    print(f"Training data shape:")
    print(f"  Energy: {energy_shape}")
    print(f"  Gradients: {train_data['gradients'].shape}")

    # Determine input shape (H, W)
    input_shape = (energy_shape[2], energy_shape[3])

    if args.use_ace:
        # ACE-enhanced training
        agent, socratic_config = create_ace_agent(
            args,
            input_shape,
            Path(args.checkpoint_path) if args.checkpoint_path else None
        )

        history = train_with_ace(
            args,
            agent,
            socratic_config,
            train_data
        )
    else:
        # Standard training (S2 trainer)
        print("\nUsing standard training (no ACE)...")
        from phase4.nvp.trainer import Trainer, TrainingConfig
        from phase4.nvp.nvp_model import NVPConfig

        config = TrainingConfig(
            model_config=NVPConfig(latent_dim=args.latent_dim),
            batch_size=args.batch_size,
            num_epochs=args.epochs,
            learning_rate=args.learning_rate,
            input_shape=input_shape
        )

        trainer = Trainer(config)
        history = trainer.train(train_data, verbose=args.verbose)

    # Save checkpoint
    if args.use_ace:
        final_metrics = {
            'confidence': history[-1]['mean_confidence'],
            'energy_fidelity': history[-1]['mean_fidelity'],
            'entropy_coherence': history[-1]['mean_entropy'],
            'aspiration_rate': history[-1]['aspiration_rate']
        }

        checkpoint_path = save_checkpoint(
            agent,
            args,
            final_metrics,
            Path(args.checkpoint_dir)
        )

    print("\nTraining complete!")
    print(f"Logs saved to: {args.log_dir}")


if __name__ == '__main__':
    main()
