#!/usr/bin/env python3
"""
infer_ace.py
Production Inference Script with ACE Agent Integration

Enhanced inference with:
- Single/Socratic/Ensemble ACE agents
- Batch processing of energy sequences
- Confidence and uncertainty estimation
- Visualization and diagnostics
- Export with rich metadata
"""

import argparse
import sys
from pathlib import Path
import numpy as np
import jax.numpy as jnp
from jax import random
import time
from typing import Dict, List, Optional
import json

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
    EnsembleConfig,
    PredictionResult
)
from phase4.nvp.nvp_model import NVPConfig


def load_domain_sequences(
    domain: str,
    data_dir: Path,
    max_sequences: int = None
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
        description='Run inference with ACE cognitive architecture'
    )

    # Data
    parser.add_argument('--domain', type=str, default='plasma_physics',
                       help='Domain to infer on')
    parser.add_argument('--data-path', type=str, default=None,
                       help='Path to energy atlas data')
    parser.add_argument('--max-sequences', type=int, default=None,
                       help='Maximum sequences to process')

    # Model
    parser.add_argument('--checkpoint', type=str, required=True,
                       help='Path to trained model checkpoint')
    parser.add_argument('--agent-type', type=str, default='ace',
                       choices=['ace', 'socratic', 'ensemble'],
                       help='Type of ACE agent')
    parser.add_argument('--latent-dim', type=int, default=128,
                       help='Latent dimension')

    # ACE Configuration
    parser.add_argument('--target-fidelity', type=float, default=0.90,
                       help='Target energy fidelity')
    parser.add_argument('--target-entropy', type=float, default=0.85,
                       help='Target entropy coherence')
    parser.add_argument('--min-confidence', type=float, default=0.70,
                       help='Minimum prediction confidence')

    # Socratic (if enabled)
    parser.add_argument('--socratic-iterations', type=int, default=3,
                       help='Max Socratic correction iterations')

    # Ensemble (if enabled)
    parser.add_argument('--ensemble-models', type=str, nargs='+',
                       help='Paths to ensemble model checkpoints (for ensemble mode)')

    # Output
    parser.add_argument('--output-dir', type=str, default='inference_results',
                       help='Directory for output results')
    parser.add_argument('--save-predictions', action='store_true',
                       help='Save prediction arrays')
    parser.add_argument('--save-uncertainty', action='store_true',
                       help='Save uncertainty maps')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualizations')

    # Logging
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    return parser.parse_args()


def load_ace_agent(
    args,
    input_shape: tuple
) -> ACEAgent:
    """
    Load ACE agent from checkpoint.

    Args:
        args: Command-line arguments
        input_shape: Input shape (H, W)

    Returns:
        Loaded ACE agent
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
            use_ensemble=(args.agent_type == 'ensemble'),
            ensemble_size=3 if args.agent_type == 'ensemble' else 1
        ),
        execution=ExecutionConfig(
            nvp_config=nvp_config,
            input_shape=input_shape,
            enforce_energy_conservation=True,
            enforce_entropy_monotonicity=True
        )
    )

    checkpoint_path = Path(args.checkpoint)

    # Create agent based on type
    if args.agent_type == 'ensemble':
        ensemble_config = EnsembleConfig(
            num_models=3,
            consensus_method="median",
            max_disagreement=0.2
        )

        # Use provided ensemble model paths or default to single checkpoint
        model_paths = args.ensemble_models if args.ensemble_models else None

        agent = EnsembleACEAgent(
            ace_config,
            ensemble_config,
            model_paths=model_paths
        )

        print(f"Loaded Ensemble ACE Agent with {ensemble_config.num_models} models")

    elif args.agent_type == 'socratic':
        socratic_config = SocraticConfig(
            max_iterations=args.socratic_iterations,
            verbose=args.verbose
        )

        agent = SocraticACEAgent(
            ace_config,
            socratic_config,
            model_path=checkpoint_path
        )

        print(f"Loaded Socratic ACE Agent (max iterations: {args.socratic_iterations})")

    else:
        agent = ACEAgent(ace_config, model_path=checkpoint_path)
        print("Loaded ACE Agent")

    return agent


def run_inference(
    args,
    agent: ACEAgent,
    sequences: List[np.ndarray]
) -> Dict:
    """
    Run inference on energy sequences.

    Args:
        args: Command-line arguments
        agent: ACE agent
        sequences: List of energy sequences (N, T, H, W)

    Returns:
        Dictionary with inference results
    """
    print("\n" + "="*60)
    print("ACE INFERENCE")
    print("="*60)
    print(f"Agent Type: {type(agent).__name__}")
    print(f"Sequences: {len(sequences)}")
    print(f"Target Fidelity: {args.target_fidelity}")
    print(f"Target Entropy: {args.target_entropy}")
    print(f"Min Confidence: {args.min_confidence}")
    print("="*60)

    # Prepare storage
    all_results = []
    predictions = []
    uncertainties = []
    targets = []

    # Statistics tracking
    stats = {
        'confidence': [],
        'energy_fidelity': [],
        'entropy_coherence': [],
        'aspiration_met': [],
        'execution_time': []
    }

    # Process sequences
    total_predictions = 0
    start_time = time.time()

    for seq_idx, sequence in enumerate(sequences):
        T, H, W = sequence.shape
        print(f"\nProcessing sequence {seq_idx + 1}/{len(sequences)}")
        print(f"  Shape: {T}×{H}×{W}")

        seq_predictions = []
        seq_uncertainties = []
        seq_targets = []

        # Predict each timestep
        for t in range(T - 1):
            energy_t = sequence[t]
            energy_target = sequence[t + 1]

            # Compute gradients
            grad_x = np.gradient(energy_t, axis=1)
            grad_y = np.gradient(energy_t, axis=0)

            # Make prediction
            if isinstance(agent, SocraticACEAgent):
                # Use Socratic correction
                result, history = agent.predict_with_correction(
                    energy_t, grad_x, grad_y, energy_target
                )
            else:
                # Standard prediction
                result = agent.predict(energy_t, grad_x, grad_y, energy_target)

            # Store results
            seq_predictions.append(result.energy_pred)
            seq_uncertainties.append(result.uncertainty)
            seq_targets.append(energy_target)
            all_results.append(result)

            # Track statistics
            stats['confidence'].append(result.confidence)
            stats['energy_fidelity'].append(result.energy_fidelity)
            stats['entropy_coherence'].append(result.entropy_coherence)
            stats['aspiration_met'].append(result.aspiration_met)
            stats['execution_time'].append(result.execution_time)

            total_predictions += 1

            # Progress
            if args.verbose and (t + 1) % 10 == 0:
                print(f"  Timestep {t + 1}/{T - 1}: "
                      f"conf={result.confidence:.3f}, "
                      f"fid={result.energy_fidelity:.3f}, "
                      f"ent={result.entropy_coherence:.3f}")

        # Store sequence results
        predictions.append(np.stack(seq_predictions, axis=0))
        uncertainties.append(np.stack(seq_uncertainties, axis=0))
        targets.append(np.stack(seq_targets, axis=0))

    total_time = time.time() - start_time

    # Compute aggregate statistics
    aggregate_stats = {
        'total_predictions': total_predictions,
        'total_time': total_time,
        'mean_confidence': float(np.mean(stats['confidence'])),
        'std_confidence': float(np.std(stats['confidence'])),
        'mean_fidelity': float(np.mean(stats['energy_fidelity'])),
        'std_fidelity': float(np.std(stats['energy_fidelity'])),
        'mean_entropy': float(np.mean(stats['entropy_coherence'])),
        'std_entropy': float(np.std(stats['entropy_coherence'])),
        'aspiration_rate': float(np.mean(stats['aspiration_met'])),
        'mean_execution_time': float(np.mean(stats['execution_time'])),
        'throughput': total_predictions / total_time  # predictions/sec
    }

    # Print summary
    print("\n" + "="*60)
    print("INFERENCE COMPLETE")
    print("="*60)
    print(f"Total Predictions: {total_predictions}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Throughput: {aggregate_stats['throughput']:.2f} pred/sec")
    print(f"\nConfidence:       {aggregate_stats['mean_confidence']:.4f} ± {aggregate_stats['std_confidence']:.4f}")
    print(f"Energy Fidelity:  {aggregate_stats['mean_fidelity']:.4f} ± {aggregate_stats['std_fidelity']:.4f}")
    print(f"Entropy Coherence: {aggregate_stats['mean_entropy']:.4f} ± {aggregate_stats['std_entropy']:.4f}")
    print(f"Aspiration Rate:  {aggregate_stats['aspiration_rate']:.2%}")
    print("="*60)

    # Return comprehensive results
    return {
        'predictions': predictions,
        'uncertainties': uncertainties,
        'targets': targets,
        'results': all_results,
        'stats': aggregate_stats,
        'per_prediction_stats': stats
    }


def save_results(args, results: Dict):
    """
    Save inference results to disk.

    Args:
        args: Command-line arguments
        results: Inference results dictionary
    """
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving results to {output_dir}...")

    # Save aggregate statistics
    stats_path = output_dir / "inference_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(results['stats'], f, indent=2)
    print(f"  Saved: {stats_path}")

    # Save per-prediction statistics
    per_pred_path = output_dir / "per_prediction_stats.npz"
    np.savez(
        per_pred_path,
        confidence=np.array(results['per_prediction_stats']['confidence']),
        energy_fidelity=np.array(results['per_prediction_stats']['energy_fidelity']),
        entropy_coherence=np.array(results['per_prediction_stats']['entropy_coherence']),
        aspiration_met=np.array(results['per_prediction_stats']['aspiration_met']),
        execution_time=np.array(results['per_prediction_stats']['execution_time'])
    )
    print(f"  Saved: {per_pred_path}")

    # Save predictions (if requested)
    if args.save_predictions:
        for i, pred_seq in enumerate(results['predictions']):
            pred_path = output_dir / f"predictions_seq{i:03d}.npz"
            np.savez_compressed(
                pred_path,
                predictions=pred_seq,
                targets=results['targets'][i]
            )
        print(f"  Saved {len(results['predictions'])} prediction sequences")

    # Save uncertainty maps (if requested)
    if args.save_uncertainty:
        for i, unc_seq in enumerate(results['uncertainties']):
            unc_path = output_dir / f"uncertainty_seq{i:03d}.npz"
            np.savez_compressed(unc_path, uncertainty=unc_seq)
        print(f"  Saved {len(results['uncertainties'])} uncertainty sequences")

    print("\n✓ All results saved")


def visualize_results(args, results: Dict):
    """
    Generate visualizations of inference results.

    Args:
        args: Command-line arguments
        results: Inference results dictionary
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
    except ImportError:
        print("Warning: matplotlib not available, skipping visualization")
        return

    output_dir = Path(args.output_dir)
    viz_dir = output_dir / "visualizations"
    viz_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating visualizations in {viz_dir}...")

    # 1. Statistics distribution plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("ACE Inference Statistics", fontsize=14, fontweight='bold')

    # Confidence distribution
    axes[0, 0].hist(results['per_prediction_stats']['confidence'], bins=30, alpha=0.7, edgecolor='black')
    axes[0, 0].axvline(args.min_confidence, color='r', linestyle='--', label=f'Min Threshold ({args.min_confidence})')
    axes[0, 0].set_xlabel('Confidence')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Confidence Distribution')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Energy fidelity distribution
    axes[0, 1].hist(results['per_prediction_stats']['energy_fidelity'], bins=30, alpha=0.7, edgecolor='black', color='green')
    axes[0, 1].axvline(args.target_fidelity, color='r', linestyle='--', label=f'Target ({args.target_fidelity})')
    axes[0, 1].set_xlabel('Energy Fidelity')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Energy Fidelity Distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Entropy coherence distribution
    axes[1, 0].hist(results['per_prediction_stats']['entropy_coherence'], bins=30, alpha=0.7, edgecolor='black', color='orange')
    axes[1, 0].axvline(args.target_entropy, color='r', linestyle='--', label=f'Target ({args.target_entropy})')
    axes[1, 0].set_xlabel('Entropy Coherence')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Entropy Coherence Distribution')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Execution time distribution
    axes[1, 1].hist(results['per_prediction_stats']['execution_time'], bins=30, alpha=0.7, edgecolor='black', color='purple')
    axes[1, 1].set_xlabel('Execution Time (s)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Execution Time Distribution')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(viz_dir / "statistics_distributions.png", dpi=150)
    plt.close()
    print("  Saved: statistics_distributions.png")

    # 2. Sample prediction visualization
    if len(results['predictions']) > 0:
        # Visualize first sequence, first 3 timesteps
        pred_seq = results['predictions'][0]
        unc_seq = results['uncertainties'][0]
        target_seq = results['targets'][0]

        num_samples = min(3, len(pred_seq))

        fig = plt.figure(figsize=(15, 4 * num_samples))
        gs = gridspec.GridSpec(num_samples, 4, figure=fig)

        for i in range(num_samples):
            # Target
            ax1 = fig.add_subplot(gs[i, 0])
            im1 = ax1.imshow(target_seq[i], cmap='hot', aspect='auto')
            ax1.set_title(f'Target (t={i+1})')
            ax1.axis('off')
            plt.colorbar(im1, ax=ax1, fraction=0.046)

            # Prediction
            ax2 = fig.add_subplot(gs[i, 1])
            im2 = ax2.imshow(pred_seq[i], cmap='hot', aspect='auto')
            ax2.set_title(f'Prediction (t={i+1})')
            ax2.axis('off')
            plt.colorbar(im2, ax=ax2, fraction=0.046)

            # Error
            ax3 = fig.add_subplot(gs[i, 2])
            error = np.abs(pred_seq[i] - target_seq[i])
            im3 = ax3.imshow(error, cmap='viridis', aspect='auto')
            ax3.set_title(f'Absolute Error (t={i+1})')
            ax3.axis('off')
            plt.colorbar(im3, ax=ax3, fraction=0.046)

            # Uncertainty
            ax4 = fig.add_subplot(gs[i, 3])
            im4 = ax4.imshow(unc_seq[i], cmap='plasma', aspect='auto')
            ax4.set_title(f'Uncertainty (t={i+1})')
            ax4.axis('off')
            plt.colorbar(im4, ax=ax4, fraction=0.046)

        plt.tight_layout()
        plt.savefig(viz_dir / "sample_predictions.png", dpi=150)
        plt.close()
        print("  Saved: sample_predictions.png")

    print("\n✓ Visualizations complete")


def main():
    """Main inference script."""
    args = parse_args()

    print("="*60)
    print("ACE INFERENCE PIPELINE")
    print("="*60)
    print(f"Domain: {args.domain}")
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Agent Type: {args.agent_type}")
    print(f"Output: {args.output_dir}")

    # Verify checkpoint exists
    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.exists():
        print(f"\nERROR: Checkpoint not found: {checkpoint_path}")
        print("Please provide a valid checkpoint path with --checkpoint")
        return

    # Load data
    print("\nLoading energy sequences...")
    data_dir = Path(args.data_path) if args.data_path else Path.cwd() / "data"

    # Load sequences for domain
    sequences, _ = load_domain_sequences(
        domain=args.domain,
        data_dir=data_dir,
        max_sequences=args.max_sequences
    )

    print(f"Loaded {len(sequences)} sequences")

    if len(sequences) == 0:
        print("ERROR: No sequences loaded!")
        return

    # Determine input shape from first sequence
    input_shape = (sequences[0].shape[1], sequences[0].shape[2])  # (H, W)
    print(f"Input shape: {input_shape}")

    # Load ACE agent
    print("\nLoading ACE agent...")
    agent = load_ace_agent(args, input_shape)

    # Run inference
    results = run_inference(args, agent, sequences)

    # Save results
    save_results(args, results)

    # Generate visualizations (if requested)
    if args.visualize:
        visualize_results(args, results)

    print("\n✓ Inference pipeline complete!")


if __name__ == '__main__':
    main()
