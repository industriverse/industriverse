#!/usr/bin/env python3
"""
train_nvp.py
Example training script for NVP model.

Usage:
    python train_nvp.py --domain plasma_physics --epochs 50
"""

import argparse
import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from phase4.core.atlas_loader import EnergyAtlasLoader
from phase4.nvp.nvp_model import NVPConfig
from phase4.nvp.trainer import Trainer, TrainingConfig, prepare_training_data


def load_domain_sequences(
    domain: str,
    data_dir: Path,
    max_sequences: int = 10
) -> list:
    """Load energy map sequences for a domain."""
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
        if len(sequences) >= max_sequences:
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


def main():
    parser = argparse.ArgumentParser(description="Train NVP model")
    parser.add_argument('--domain', type=str, default='plasma_physics',
                       help='Physics domain to train on')
    parser.add_argument('--data-dir', type=str, default='data',
                       help='Data directory')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=8,
                       help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-4,
                       help='Learning rate')
    parser.add_argument('--checkpoint-dir', type=str, default='phase4/checkpoints',
                       help='Checkpoint directory')
    parser.add_argument('--max-sequences', type=int, default=20,
                       help='Maximum number of sequences to load')

    args = parser.parse_args()

    print(f"Training NVP model on domain: {args.domain}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size}")
    print(f"Learning rate: {args.lr}")
    print("")

    # Determine workspace root
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent
    data_dir = workspace_root / args.data_dir

    # Load sequences
    print("Loading energy map sequences...")
    sequences, loader = load_domain_sequences(
        args.domain,
        data_dir,
        max_sequences=args.max_sequences
    )
    print(f"Loaded {len(sequences)} sequences")

    if len(sequences) == 0:
        print("Error: No sequences loaded!")
        return

    # Prepare training data
    print("Preparing training data (computing gradients)...")
    train_data = prepare_training_data(sequences, loader)

    print(f"Training data shape:")
    print(f"  Energy: {train_data['energy_sequence'].shape}")
    print(f"  Gradients: {train_data['gradients'].shape}")
    print("")

    # Create model config
    model_config = NVPConfig(
        latent_dim=512,
        encoder_features=[64, 128, 256],
        decoder_features=[256, 128, 64],
        use_residual=True,
        use_batch_norm=True,
        dropout_rate=0.1
    )

    # Create training config
    training_config = TrainingConfig(
        model_config=model_config,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        learning_rate=args.lr,
        lambda_conservation=0.1,
        lambda_entropy=0.05,
        checkpoint_dir=str(workspace_root / args.checkpoint_dir),
        checkpoint_every=10,
        log_dir=str(workspace_root / "phase4" / "logs"),
        input_shape=(256, 256),
        seed=42
    )

    # Create trainer
    print("Initializing trainer...")
    trainer = Trainer(training_config)

    # Train
    print("Starting training...")
    print("=" * 60)
    history = trainer.train(train_data, val_data=None, verbose=True)

    print("=" * 60)
    print("Training complete!")
    print("")

    # Print final metrics
    final_metrics = history['train'][-1]
    print("Final Training Metrics:")
    print(f"  Total Loss: {final_metrics.loss_total:.4f}")
    print(f"  MSE Loss: {final_metrics.loss_mse:.4f}")
    print(f"  Conservation Loss: {final_metrics.loss_conservation:.4f}")
    print(f"  Entropy Loss: {final_metrics.loss_entropy:.4f}")
    print(f"  Energy Fidelity: {final_metrics.energy_fidelity:.4f}")
    print(f"  RMSE: {final_metrics.rmse:.4f}")
    print(f"  Entropy Coherence: {final_metrics.entropy_coherence:.4f}")
    print("")

    # Success criteria
    print("Success Criteria:")
    print(f"  Energy Fidelity > 0.90: {'✓' if final_metrics.energy_fidelity > 0.90 else '✗'}")
    print(f"  RMSE < 0.1: {'✓' if final_metrics.rmse < 0.1 else '✗'}")
    print(f"  Entropy Coherence > 0.85: {'✓' if final_metrics.entropy_coherence > 0.85 else '✗'}")


if __name__ == '__main__':
    main()
