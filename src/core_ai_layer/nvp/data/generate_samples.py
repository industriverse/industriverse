#!/usr/bin/env python3
"""
generate_samples.py
Generate sample energy maps for all 5 default domains.

Creates synthetic datasets for testing and development.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from phase4.data.synthetic_generator import (
    generate_domain_dataset,
    PerturbationConfig
)

# Domain configurations
DOMAINS = {
    'plasma_physics': {
        'pattern_type': 'turbulent',
        'n_sequences': 5,
        'sequence_length': 10,
        'config': PerturbationConfig(
            rotation_range=(0, 360),
            noise_sigma=0.15,
            thermal_blur_sigma=3.0,
            enable_rotation=True,
            enable_noise=True,
            enable_thermal_blur=True,
            enable_translation=True
        )
    },
    'fluid_dynamics': {
        'pattern_type': 'vortex',
        'n_sequences': 5,
        'sequence_length': 10,
        'config': PerturbationConfig(
            rotation_range=(0, 180),
            noise_sigma=0.1,
            thermal_blur_sigma=2.0,
            enable_rotation=True,
            enable_noise=True,
            enable_thermal_blur=True,
            enable_translation=True
        )
    },
    'astrophysics': {
        'pattern_type': 'turbulent',
        'n_sequences': 5,
        'sequence_length': 10,
        'config': PerturbationConfig(
            rotation_range=(0, 360),
            noise_sigma=0.2,
            thermal_blur_sigma=4.0,
            enable_rotation=True,
            enable_noise=True,
            enable_thermal_blur=True,
            enable_translation=False
        )
    },
    'turbulent_radiative_layer': {
        'pattern_type': 'turbulent',
        'n_sequences': 5,
        'sequence_length': 10,
        'config': PerturbationConfig(
            rotation_range=(0, 90),
            noise_sigma=0.12,
            thermal_blur_sigma=2.5,
            enable_rotation=True,
            enable_noise=True,
            enable_thermal_blur=True,
            enable_translation=True
        )
    },
    'active_matter': {
        'pattern_type': 'vortex',
        'n_sequences': 5,
        'sequence_length': 10,
        'config': PerturbationConfig(
            rotation_range=(0, 360),
            noise_sigma=0.08,
            thermal_blur_sigma=1.5,
            enable_rotation=True,
            enable_noise=True,
            enable_thermal_blur=True,
            enable_translation=True
        )
    }
}


def main():
    """Generate sample datasets for all domains."""
    # Determine output directory
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent
    data_dir = workspace_root / "data" / "energy_maps"

    print(f"Generating sample energy maps...")
    print(f"Output directory: {data_dir}")
    print("")

    all_stats = {}

    for domain, params in DOMAINS.items():
        print(f"Generating {domain}...")

        stats = generate_domain_dataset(
            domain=domain,
            output_dir=data_dir,
            n_sequences=params['n_sequences'],
            sequence_length=params['sequence_length'],
            pattern_type=params['pattern_type'],
            size=256,
            config=params['config']
        )

        all_stats[domain] = stats

        print(f"  ✓ Generated {stats['total_maps']} maps")
        print(f"    Energy: {stats['energy_mean']:.3f} ± {stats['energy_std']:.3f}")
        print(f"    Entropy: {stats['entropy_mean']:.3f} ± {stats['entropy_std']:.3f}")
        print("")

    # Save summary
    import json
    summary_path = data_dir / "generation_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(all_stats, f, indent=2)

    print(f"✅ Generation complete!")
    print(f"Summary saved to: {summary_path}")
    print(f"Total maps generated: {sum(s['total_maps'] for s in all_stats.values())}")


if __name__ == '__main__':
    main()
