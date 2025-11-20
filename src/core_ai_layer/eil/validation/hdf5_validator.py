#!/usr/bin/env python3
"""
HDF5 Validator - Ground Truth Physics Validation

Compares ACE predictions against real physics simulation data from HDF5 files.
Supports OpenFOAM, GROMACS, FLASH, Enzo simulation outputs.

This validator will be used when external drive with real physics datasets
is connected to validate whether the model learns real physics vs patterns.

Critical for answering: "Is this real physics or just pattern matching?"
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

import numpy as np
import h5py

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from phase5.validation.metrics import (
    compute_energy_fidelity,
    compute_entropy_coherence,
    compute_prediction_mse,
    compute_spectral_similarity,
    compute_physics_validation_suite
)


class HDF5Validator:
    """
    Validate ACE predictions against ground truth HDF5 simulation data

    Supports multiple simulation formats:
    - OpenFOAM: /energy_maps or /U (velocity), /p (pressure)
    - GROMACS: /atom_positions, /forces, /energy
    - FLASH/Enzo: /density, /velocity, /temperature
    """

    def __init__(self, model):
        """
        Initialize validator

        Args:
            model: ACE model or Shadow Ensemble for predictions
        """
        self.model = model
        print("✓ HDF5 Validator initialized")

    def validate(
        self,
        hdf5_uri: str,
        domain: str,
        num_sequences: int = 5,
        num_steps: int = 10
    ) -> Dict:
        """
        Run full validation suite against HDF5 ground truth

        Args:
            hdf5_uri: Path or S3 URI to HDF5 file
            domain: Physical domain (plasma_physics, fluid_dynamics, etc.)
            num_sequences: Number of sequences to validate
            num_steps: Number of prediction timesteps

        Returns:
            Validation report dictionary
        """
        print("\n" + "="*70)
        print("HDF5 PHYSICS VALIDATION")
        print("="*70)
        print(f"File: {hdf5_uri}")
        print(f"Domain: {domain}")
        print(f"Sequences: {num_sequences}, Steps: {num_steps}")
        print("="*70 + "\n")

        # Load HDF5 data
        try:
            ground_truth_data = self._load_hdf5(hdf5_uri, domain, num_sequences, num_steps)
        except Exception as e:
            return {
                'status': 'error',
                'error': f"Failed to load HDF5: {str(e)}",
                'hdf5_uri': hdf5_uri
            }

        # Run predictions
        predictions_data = []
        for seq_idx, gt_sequence in enumerate(ground_truth_data['sequences']):
            try:
                # Use first timestep as initial condition
                initial_state = gt_sequence[0]

                # Predict sequence
                if hasattr(self.model, 'predict'):
                    result = self.model.predict(
                        energy_map=initial_state,
                        domain=domain,
                        num_steps=num_steps,
                        mode='ensemble',
                        return_confidence=True
                    )
                    predictions = result['predictions']
                else:
                    # Fallback for simple models
                    predictions = self._run_simple_prediction(initial_state, num_steps)

                predictions_data.append(predictions)

            except Exception as e:
                print(f"⚠️  Sequence {seq_idx} prediction failed: {e}")
                continue

        if not predictions_data:
            return {
                'status': 'error',
                'error': 'All predictions failed',
                'hdf5_uri': hdf5_uri
            }

        # Compute validation metrics
        metrics = self._compute_validation_metrics(
            predictions=predictions_data,
            ground_truth=ground_truth_data['sequences'],
            domain=domain
        )

        # Generate report
        report = {
            'status': 'success',
            'hdf5_uri': hdf5_uri,
            'domain': domain,
            'num_sequences': len(predictions_data),
            'num_steps': num_steps,
            'metrics': metrics,
            'ground_truth_metadata': ground_truth_data['metadata'],
            'validation_timestamp': ground_truth_data['timestamp'],
            'assessment': self._assess_results(metrics)
        }

        self._print_report(report)

        return report

    def _load_hdf5(
        self,
        hdf5_uri: str,
        domain: str,
        num_sequences: int,
        num_steps: int
    ) -> Dict:
        """
        Load ground truth data from HDF5 file

        Handles different simulation formats and extracts relevant fields.
        """
        import time

        # Handle S3 URIs (TODO: implement S3 support)
        if hdf5_uri.startswith('s3://'):
            raise NotImplementedError("S3 URIs not yet supported. Use local paths for now.")

        # Open HDF5 file
        with h5py.File(hdf5_uri, 'r') as f:
            # Detect format and extract data
            if 'energy_maps' in f:
                # Direct energy map format (simplest)
                data = f['energy_maps'][:]
            elif 'U' in f and 'p' in f:
                # OpenFOAM format (velocity + pressure)
                velocity = f['U'][:]
                pressure = f['p'][:]
                # Convert to energy: E = 0.5 * ρ * v² + p
                data = 0.5 * velocity**2 + pressure
            elif 'density' in f:
                # FLASH/Enzo format
                density = f['density'][:]
                if 'temperature' in f:
                    temperature = f['temperature'][:]
                    # Thermal energy
                    data = density * temperature
                else:
                    data = density
            elif 'atom_positions' in f:
                # GROMACS format
                positions = f['atom_positions'][:]
                # Compute energy maps from positions (simplified)
                data = self._positions_to_energy_maps(positions)
            else:
                raise ValueError(f"Unknown HDF5 format. Available keys: {list(f.keys())}")

            # Extract metadata
            metadata = {
                'format': 'detected_format',
                'shape': data.shape,
                'dtype': str(data.dtype),
                'total_timesteps': data.shape[0] if data.ndim >= 3 else 1
            }

            # Extract sequences
            sequences = self._extract_sequences(data, num_sequences, num_steps)

        return {
            'sequences': sequences,
            'metadata': metadata,
            'timestamp': time.time()
        }

    def _extract_sequences(
        self,
        data: np.ndarray,
        num_sequences: int,
        num_steps: int
    ) -> List[np.ndarray]:
        """Extract non-overlapping sequences from time series data"""
        sequences = []

        # Handle different data shapes
        if data.ndim == 3:
            # (time, height, width)
            total_time = data.shape[0]
        elif data.ndim == 4:
            # (time, depth, height, width) - take 2D slice
            data = data[:, data.shape[1]//2, :, :]  # Middle slice
            total_time = data.shape[0]
        else:
            raise ValueError(f"Unexpected data shape: {data.shape}")

        # Extract sequences
        stride = num_steps
        for start in range(0, total_time - num_steps, stride):
            if len(sequences) >= num_sequences:
                break

            sequence = data[start:start+num_steps]

            # Resize to 256x256 if needed
            if sequence.shape[1:] != (256, 256):
                sequence = self._resize_sequence(sequence, target_size=256)

            sequences.append(sequence)

        return sequences

    def _resize_sequence(self, sequence: np.ndarray, target_size: int) -> np.ndarray:
        """Resize sequence to target spatial resolution"""
        from scipy.ndimage import zoom

        time_steps = sequence.shape[0]
        current_size = sequence.shape[1]
        zoom_factor = target_size / current_size

        resized = np.zeros((time_steps, target_size, target_size), dtype=sequence.dtype)
        for t in range(time_steps):
            resized[t] = zoom(sequence[t], zoom_factor, order=1)

        return resized

    def _positions_to_energy_maps(self, positions: np.ndarray) -> np.ndarray:
        """Convert GROMACS atom positions to energy density maps"""
        # Simplified: create density histogram
        # TODO: Implement proper energy computation from MD trajectories
        time_steps = positions.shape[0]
        maps = []

        for t in range(time_steps):
            # Histogram positions into 2D grid
            hist, _, _ = np.histogram2d(
                positions[t, :, 0],
                positions[t, :, 1],
                bins=256,
                range=[[0, 100], [0, 100]]
            )
            maps.append(hist)

        return np.array(maps)

    def _run_simple_prediction(
        self,
        initial_state: np.ndarray,
        num_steps: int
    ) -> np.ndarray:
        """Fallback simple prediction for models without predict() method"""
        # Naive forward integration (placeholder)
        predictions = np.zeros((num_steps, *initial_state.shape), dtype=np.float32)
        predictions[0] = initial_state

        for t in range(1, num_steps):
            # Simple diffusion-like update
            predictions[t] = predictions[t-1] * 0.99 + np.roll(predictions[t-1], 1, axis=0) * 0.01

        return predictions

    def _compute_validation_metrics(
        self,
        predictions: List[np.ndarray],
        ground_truth: List[np.ndarray],
        domain: str
    ) -> Dict:
        """Compute comprehensive validation metrics"""
        metrics = {
            'per_sequence': [],
            'aggregate': {}
        }

        all_mse = []
        all_fidelity = []
        all_entropy = []
        all_spectral = []

        for pred, gt in zip(predictions, ground_truth):
            # Per-sequence metrics
            seq_metrics = {
                'mse': compute_prediction_mse(pred, gt),
                'energy_fidelity': compute_energy_fidelity(pred, reference=gt[0]),
                'entropy_coherence': compute_entropy_coherence(pred),
                'spectral_similarity': compute_spectral_similarity(pred, gt)
            }

            metrics['per_sequence'].append(seq_metrics)

            all_mse.append(seq_metrics['mse'])
            all_fidelity.append(seq_metrics['energy_fidelity'])
            all_entropy.append(seq_metrics['entropy_coherence'])
            all_spectral.append(seq_metrics['spectral_similarity'])

        # Aggregate statistics
        metrics['aggregate'] = {
            'mean_mse': float(np.mean(all_mse)),
            'std_mse': float(np.std(all_mse)),
            'mean_energy_fidelity': float(np.mean(all_fidelity)),
            'std_energy_fidelity': float(np.std(all_fidelity)),
            'mean_entropy_coherence': float(np.mean(all_entropy)),
            'std_entropy_coherence': float(np.std(all_entropy)),
            'mean_spectral_similarity': float(np.mean(all_spectral)),
            'std_spectral_similarity': float(np.std(all_spectral))
        }

        return metrics

    def _assess_results(self, metrics: Dict) -> Dict:
        """
        Assess validation results and provide verdict

        Critical analysis: Real physics vs pattern matching?
        """
        agg = metrics['aggregate']

        mse = agg['mean_mse']
        fidelity = agg['mean_energy_fidelity']
        entropy = agg['mean_entropy_coherence']
        spectral = agg['mean_spectral_similarity']

        # Thresholds for assessment
        EXCELLENT_MSE = 0.01
        GOOD_MSE = 0.05
        EXCELLENT_SPECTRAL = 0.9
        GOOD_SPECTRAL = 0.7

        assessment = {
            'overall_grade': 'UNKNOWN',
            'physical_accuracy': 'UNKNOWN',
            'concerns': [],
            'strengths': [],
            'recommendations': []
        }

        # Assess MSE
        if mse < EXCELLENT_MSE:
            assessment['strengths'].append(f"Excellent MSE ({mse:.4f}) - predictions very close to ground truth")
            mse_grade = 'EXCELLENT'
        elif mse < GOOD_MSE:
            assessment['strengths'].append(f"Good MSE ({mse:.4f}) - acceptable prediction accuracy")
            mse_grade = 'GOOD'
        else:
            assessment['concerns'].append(f"High MSE ({mse:.4f}) - predictions deviate significantly from ground truth")
            mse_grade = 'POOR'

        # Assess spectral similarity (critical for physics)
        if spectral > EXCELLENT_SPECTRAL:
            assessment['strengths'].append(f"Excellent spectral similarity ({spectral:.4f}) - captures energy cascade")
            spectral_grade = 'EXCELLENT'
        elif spectral > GOOD_SPECTRAL:
            assessment['strengths'].append(f"Good spectral similarity ({spectral:.4f}) - reasonable energy distribution")
            spectral_grade = 'GOOD'
        else:
            assessment['concerns'].append(f"Low spectral similarity ({spectral:.4f}) - may not capture physics correctly")
            spectral_grade = 'POOR'

        # Assess energy conservation
        if fidelity > 0.95:
            assessment['strengths'].append(f"Strong energy conservation ({fidelity:.4f})")
        elif fidelity > 0.85:
            assessment['concerns'].append(f"Moderate energy drift ({fidelity:.4f})")
        else:
            assessment['concerns'].append(f"Significant energy violation ({fidelity:.4f}) - breaks physics")

        # Overall verdict
        if mse_grade == 'EXCELLENT' and spectral_grade == 'EXCELLENT':
            assessment['overall_grade'] = 'EXCELLENT'
            assessment['physical_accuracy'] = 'REAL_PHYSICS'
            assessment['recommendations'].append("Model demonstrates real physics understanding. Safe for production use.")
        elif mse_grade in ['EXCELLENT', 'GOOD'] and spectral_grade in ['EXCELLENT', 'GOOD']:
            assessment['overall_grade'] = 'GOOD'
            assessment['physical_accuracy'] = 'GOOD_PHYSICS'
            assessment['recommendations'].append("Model shows good physics accuracy. Consider production deployment with monitoring.")
        else:
            assessment['overall_grade'] = 'POOR'
            assessment['physical_accuracy'] = 'PATTERN_MATCHING'
            assessment['recommendations'].append("Model may be pattern matching rather than learning physics. More training recommended.")
            assessment['recommendations'].append("Increase training data diversity and domain coverage.")

        return assessment

    def _print_report(self, report: Dict):
        """Pretty-print validation report"""
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70 + "\n")

        print(f"Status: {report['status']}")
        print(f"Domain: {report['domain']}")
        print(f"Sequences Validated: {report['num_sequences']}")
        print(f"Steps per Sequence: {report['num_steps']}")

        print("\nAggregate Metrics:")
        print("-" * 70)
        agg = report['metrics']['aggregate']
        print(f"  Mean MSE:               {agg['mean_mse']:.6f} ± {agg['std_mse']:.6f}")
        print(f"  Energy Fidelity:        {agg['mean_energy_fidelity']:.4f} ± {agg['std_energy_fidelity']:.4f}")
        print(f"  Entropy Coherence:      {agg['mean_entropy_coherence']:.4f} ± {agg['std_entropy_coherence']:.4f}")
        print(f"  Spectral Similarity:    {agg['mean_spectral_similarity']:.4f} ± {agg['std_spectral_similarity']:.4f}")

        print("\nAssessment:")
        print("-" * 70)
        assessment = report['assessment']
        print(f"  Overall Grade:          {assessment['overall_grade']}")
        print(f"  Physical Accuracy:      {assessment['physical_accuracy']}")

        if assessment['strengths']:
            print("\n  Strengths:")
            for strength in assessment['strengths']:
                print(f"    ✓ {strength}")

        if assessment['concerns']:
            print("\n  Concerns:")
            for concern in assessment['concerns']:
                print(f"    ⚠️  {concern}")

        if assessment['recommendations']:
            print("\n  Recommendations:")
            for rec in assessment['recommendations']:
                print(f"    → {rec}")

        print("\n" + "="*70 + "\n")


# ============================================================================
# Testing
# ============================================================================

def test_hdf5_validator():
    """Test HDF5 validator with synthetic data"""
    print("\n" + "="*70)
    print("HDF5 VALIDATOR TEST")
    print("="*70 + "\n")

    # Create synthetic HDF5 file
    import tempfile
    import h5py

    with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as tmp:
        tmp_path = tmp.name

    # Create test HDF5 with energy maps
    with h5py.File(tmp_path, 'w') as f:
        # Synthetic energy maps (20 timesteps, 256x256)
        data = np.random.rand(20, 256, 256).astype(np.float32)
        f.create_dataset('energy_maps', data=data)

    print(f"Created test HDF5: {tmp_path}")

    # Mock model
    class MockModel:
        def predict(self, energy_map, domain, num_steps, mode, return_confidence):
            # Simple forward diffusion
            preds = np.zeros((num_steps, *energy_map.shape), dtype=np.float32)
            preds[0] = energy_map
            for t in range(1, num_steps):
                preds[t] = preds[t-1] * 0.99 + np.random.rand(*energy_map.shape) * 0.01
            return {'predictions': preds}

    # Run validation
    validator = HDF5Validator(MockModel())
    report = validator.validate(
        hdf5_uri=tmp_path,
        domain='fluid_dynamics',
        num_sequences=3,
        num_steps=5
    )

    # Cleanup
    Path(tmp_path).unlink()

    print("✓ HDF5 Validator test complete")
    print(f"  Overall Grade: {report['assessment']['overall_grade']}")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_hdf5_validator()
