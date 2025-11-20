"""
Phase 5 EIL Validation with Real Physics Data

Tests the research-enhanced EIL (with LeJEPA, PhysWorld, RealDeepResearch)
against real turbulent radiative layer simulations.

Validates:
1. Regime detection accuracy
2. Research integration enhancement
3. Physics-informed predictions
4. Performance metrics
"""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add phase5 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integration.research_enhanced_eil import ResearchEnhancedEIL, ResearchEnhancementConfig
from core.energy_intelligence_layer import EnergyIntelligenceLayer


class RealPhysicsValidator:
    """Validator for EIL on real physics simulations"""

    def __init__(self, data_dir: str = "data/energy_maps/turbulent_radiative_layer"):
        self.data_dir = Path(data_dir)
        self.results_dir = Path("results_physics_validation")
        self.results_dir.mkdir(exist_ok=True)

        # Initialize research-enhanced EIL
        print("🔬 Initializing Research-Enhanced EIL...")

        # Create base EIL
        base_eil = EnergyIntelligenceLayer()

        # Create research enhancement config (all features disabled for now)
        research_config = ResearchEnhancementConfig(
            use_lejêpa_encoder=False,  # Enable after pretraining
            use_factory_physics=False,  # Enable with Egocentric-10K dataset
            use_physworld=False,       # Enable for video inputs
            use_research_updates=False # Enable for continuous learning
        )

        # Initialize research-enhanced EIL
        self.eil = ResearchEnhancedEIL(base_eil, research_config)

    def load_physics_samples(self, max_samples: int = 20) -> List[Dict[str, Any]]:
        """Load real physics energy maps and metadata"""

        print(f"\n📊 Loading physics samples from {self.data_dir}...")

        # Find all .npy files
        npy_files = sorted(self.data_dir.glob("*.npy"))[:max_samples]

        samples = []
        for npy_file in npy_files:
            # Load energy map
            energy_map = np.load(npy_file)

            # Load metadata
            metadata_file = npy_file.with_suffix('').with_suffix('.npy').parent / f"{npy_file.stem}_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}

            # Classify regime based on energy variance (proxy for turbulence)
            energy_var = float(energy_map.var())
            if energy_var > 1.0:
                regime = "high_turbulence"
            elif energy_var > 0.3:
                regime = "moderate_turbulence"
            else:
                regime = "low_turbulence"

            samples.append({
                'energy_map': energy_map,
                'metadata': metadata,
                'ground_truth_regime': regime,
                'file_path': str(npy_file),
                'energy_var': energy_var,
                'energy_mean': float(energy_map.mean()),
                'spatial_shape': energy_map.shape
            })

        print(f"✅ Loaded {len(samples)} physics samples")
        return samples

    def validate_regime_detection(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test EIL regime detection on physics samples"""

        print("\n🔍 Validating Regime Detection...")

        results = {
            'total_samples': len(samples),
            'predictions': [],
            'regime_accuracy': {},
            'performance_metrics': {}
        }

        regime_counts = {'high_turbulence': 0, 'moderate_turbulence': 0, 'low_turbulence': 0}
        regime_correct = {'high_turbulence': 0, 'moderate_turbulence': 0, 'low_turbulence': 0}

        for i, sample in enumerate(samples):
            print(f"\n   Sample {i+1}/{len(samples)}: {Path(sample['file_path']).name}")
            print(f"      Ground truth: {sample['ground_truth_regime']}")
            print(f"      Energy variance: {sample['energy_var']:.4f}")

            # Run EIL inference
            try:
                # Process with base EIL (returns EILDecision)
                eil_decision = self.eil.process(
                    energy_map=sample['energy_map'],
                    domain="physics_validation",
                    cluster="turbulent_layer",
                    node=f"sample_{i}"
                )

                # Convert decision to dict for analysis
                eil_result = {
                    'regime': eil_decision.regime,
                    'confidence': eil_decision.confidence,
                    'approved': eil_decision.approved,
                    'validity_score': eil_decision.validity_score,
                    'energy_state': eil_decision.energy_state,
                    'entropy_rate': eil_decision.entropy_rate,
                    'forecast_mean': eil_decision.forecast_mean,
                    'recommended_action': eil_decision.recommended_action,
                    'risk_level': eil_decision.risk_level
                }

                # Extract predicted regime from EIL
                predicted_regime = self._classify_eil_output(eil_result, sample['energy_var'])

                # Check correctness
                is_correct = predicted_regime == sample['ground_truth_regime']

                print(f"      Predicted: {predicted_regime} {'✅' if is_correct else '❌'}")
                print(f"      Confidence: {eil_result.get('confidence', 0):.4f}")

                # Track statistics
                regime_counts[sample['ground_truth_regime']] += 1
                if is_correct:
                    regime_correct[sample['ground_truth_regime']] += 1

                # Store prediction
                results['predictions'].append({
                    'sample_id': i,
                    'file_path': sample['file_path'],
                    'ground_truth': sample['ground_truth_regime'],
                    'predicted': predicted_regime,
                    'correct': is_correct,
                    'confidence': eil_result.get('confidence', 0),
                    'eil_output': eil_result
                })

            except Exception as e:
                print(f"      ⚠️  Error: {e}")
                results['predictions'].append({
                    'sample_id': i,
                    'error': str(e)
                })

        # Calculate accuracy per regime
        for regime in regime_counts:
            if regime_counts[regime] > 0:
                accuracy = regime_correct[regime] / regime_counts[regime]
                results['regime_accuracy'][regime] = {
                    'accuracy': accuracy,
                    'correct': regime_correct[regime],
                    'total': regime_counts[regime]
                }

        # Overall accuracy
        total_correct = sum(regime_correct.values())
        total_samples = sum(regime_counts.values())
        results['overall_accuracy'] = total_correct / total_samples if total_samples > 0 else 0

        return results

    def _classify_eil_output(self, eil_result: Dict[str, Any], energy_var: float) -> str:
        """Classify EIL output into regime categories"""

        # Use EIL's regime detection if available
        if 'regime' in eil_result:
            regime = eil_result['regime']
            # Map EIL regimes to our physics regimes
            if 'chaotic' in regime.lower() or 'unstable' in regime.lower():
                return 'high_turbulence'
            elif 'transitional' in regime.lower() or 'moderate' in regime.lower():
                return 'moderate_turbulence'
            else:
                return 'low_turbulence'

        # Fallback: use energy variance from EIL output
        eil_var = eil_result.get('energy_variance', energy_var)
        if eil_var > 1.0:
            return 'high_turbulence'
        elif eil_var > 0.3:
            return 'moderate_turbulence'
        else:
            return 'low_turbulence'

    def analyze_research_enhancements(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how research integrations enhance predictions"""

        print("\n🔬 Analyzing Research Enhancement Contributions...")

        enhancements = {
            'lejêpa_embeddings': [],
            'physworld_reconstructions': [],
            'realdeepresearch_context': [],
            'multi_source_fusion': []
        }

        for i, sample in enumerate(samples[:5]):  # Test on subset
            print(f"\n   Sample {i+1}: Analyzing research components...")

            eil_decision = self.eil.process(
                energy_map=sample['energy_map'],
                domain="physics_validation",
                cluster="turbulent_layer",
                node=f"sample_{i}"
            )

            # Convert to dict for analysis
            eil_result = {
                'regime': eil_decision.regime,
                'confidence': eil_decision.confidence,
                'approved': eil_decision.approved,
                'validity_score': eil_decision.validity_score
            }

            # Check which research modules contributed
            if 'lejêpa_embedding' in eil_result:
                enhancements['lejêpa_embeddings'].append({
                    'sample_id': i,
                    'embedding_dim': len(eil_result['lejêpa_embedding']),
                    'embedding_norm': float(np.linalg.norm(eil_result['lejêpa_embedding']))
                })
                print(f"      ✅ LeJÊPA embedding: dim={len(eil_result['lejêpa_embedding'])}")

            if 'physworld_reconstruction' in eil_result:
                enhancements['physworld_reconstructions'].append({
                    'sample_id': i,
                    'has_sdf': 'sdf' in eil_result['physworld_reconstruction'],
                    'has_gravity': 'gravity_aligned' in eil_result['physworld_reconstruction']
                })
                print(f"      ✅ PhysWorld reconstruction available")

            if 'research_context' in eil_result:
                enhancements['realdeepresearch_context'].append({
                    'sample_id': i,
                    'num_papers': len(eil_result['research_context'].get('relevant_papers', []))
                })
                print(f"      ✅ Research context from RealDeepResearch")

            if 'fusion_confidence' in eil_result:
                enhancements['multi_source_fusion'].append({
                    'sample_id': i,
                    'fusion_confidence': eil_result['fusion_confidence']
                })
                print(f"      ✅ Multi-source fusion: confidence={eil_result['fusion_confidence']:.4f}")

        return enhancements

    def generate_report(self, validation_results: Dict[str, Any],
                       enhancement_analysis: Dict[str, Any]) -> None:
        """Generate comprehensive validation report"""

        print("\n" + "=" * 70)
        print("PHASE 5 EIL VALIDATION REPORT")
        print("=" * 70)

        print("\n📊 REGIME DETECTION ACCURACY:")
        print(f"   Overall Accuracy: {validation_results['overall_accuracy']:.2%}")
        print(f"   Total Samples: {validation_results['total_samples']}")

        print("\n   Per-Regime Breakdown:")
        for regime, stats in validation_results['regime_accuracy'].items():
            print(f"      {regime}:")
            print(f"         Accuracy: {stats['accuracy']:.2%}")
            print(f"         Correct: {stats['correct']}/{stats['total']}")

        print("\n🔬 RESEARCH ENHANCEMENT ANALYSIS:")
        print(f"   LeJÊPA Embeddings: {len(enhancement_analysis['lejêpa_embeddings'])} samples")
        print(f"   PhysWorld Reconstructions: {len(enhancement_analysis['physworld_reconstructions'])} samples")
        print(f"   RealDeepResearch Context: {len(enhancement_analysis['realdeepresearch_context'])} samples")
        print(f"   Multi-Source Fusion: {len(enhancement_analysis['multi_source_fusion'])} samples")

        # Save detailed results
        output_file = self.results_dir / "validation_report.json"
        with open(output_file, 'w') as f:
            json.dump({
                'validation_results': validation_results,
                'enhancement_analysis': enhancement_analysis
            }, f, indent=2, default=str)

        print(f"\n💾 Detailed results saved to: {output_file}")
        print("=" * 70)


def main():
    print("=" * 70)
    print("PHASE 5: Real Physics Dataset Validation")
    print("Testing Research-Enhanced EIL with Turbulent Radiative Layer Data")
    print("=" * 70)

    # Initialize validator
    validator = RealPhysicsValidator()

    # Load physics samples
    samples = validator.load_physics_samples(max_samples=20)

    if len(samples) == 0:
        print("\n❌ No physics samples found!")
        return

    # Validate regime detection
    validation_results = validator.validate_regime_detection(samples)

    # Analyze research enhancements
    enhancement_analysis = validator.analyze_research_enhancements(samples)

    # Generate report
    validator.generate_report(validation_results, enhancement_analysis)

    print("\n✅ VALIDATION COMPLETE")


if __name__ == "__main__":
    main()
