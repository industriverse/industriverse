#!/usr/bin/env python3
"""
Data Catalog Audit Script
Scans data directories and generates catalog.json
"""
import json
import os
from pathlib import Path
from datetime import datetime
import hashlib
import numpy as np


def audit_data_directory(base_path: Path):
    """Audit all data files and generate catalog."""
    catalog = {
        'generated_at': datetime.now().isoformat(),
        'base_path': str(base_path),
        'maps': [],
        'telemetry': [],
        'stats': {
            'total_maps': 0,
            'total_size_mb': 0,
            'domains': set()
        }
    }

    # Scan energy maps
    maps_dir = base_path / 'energy_maps'
    if maps_dir.exists():
        for file_path in maps_dir.rglob('*.npy'):
            stat = file_path.stat()

            # Extract domain from path
            domain = file_path.parent.name if file_path.parent != maps_dir else 'unknown'

            # Load map to get statistics
            try:
                energy_map = np.load(file_path)
                energy_mean = float(np.mean(energy_map))
                energy_var = float(np.var(energy_map))
                shape = energy_map.shape
            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")
                energy_mean = None
                energy_var = None
                shape = None

            catalog['maps'].append({
                'path': str(file_path.relative_to(base_path)),
                'domain': domain,
                'size_bytes': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'sha256': hashlib.sha256(file_path.read_bytes()).hexdigest()[:16],
                'energy_mean': energy_mean,
                'energy_var': energy_var,
                'shape': shape
            })
            catalog['stats']['total_maps'] += 1
            catalog['stats']['total_size_mb'] += stat.st_size / (1024 * 1024)
            catalog['stats']['domains'].add(domain)

    # Scan telemetry
    telemetry_dir = base_path / 'telemetry'
    if telemetry_dir.exists():
        for file_path in telemetry_dir.rglob('*.*'):
            stat = file_path.stat()
            catalog['telemetry'].append({
                'path': str(file_path.relative_to(base_path)),
                'size_bytes': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    # Convert set to list for JSON serialization
    catalog['stats']['domains'] = sorted(list(catalog['stats']['domains']))

    return catalog


if __name__ == '__main__':
    workspace_root = Path(__file__).parent.parent.parent
    data_dir = workspace_root / 'data'

    print(f"Auditing data directory: {data_dir}")
    catalog = audit_data_directory(data_dir)

    # Save catalog
    catalog_path = data_dir / 'catalogs' / 'catalog.json'
    catalog_path.parent.mkdir(parents=True, exist_ok=True)

    with open(catalog_path, 'w') as f:
        json.dump(catalog, f, indent=2)

    print(f"\n✅ Catalog saved to: {catalog_path}")
    print(f"\nStatistics:")
    print(f"  Total maps: {catalog['stats']['total_maps']}")
    print(f"  Total size: {catalog['stats']['total_size_mb']:.2f} MB")
    print(f"  Domains: {', '.join(catalog['stats']['domains'])}")

    # Print per-domain breakdown
    print(f"\nPer-Domain Breakdown:")
    domain_counts = {}
    for map_info in catalog['maps']:
        domain = map_info['domain']
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    for domain in sorted(domain_counts.keys()):
        print(f"  {domain}: {domain_counts[domain]} maps")
