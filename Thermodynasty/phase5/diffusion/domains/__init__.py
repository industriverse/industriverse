"""
Domain Capsules

Specialized diffusion engines for different energy domains.
Each capsule combines the core diffusion framework with domain-specific
physics and optimization strategies.
"""

from .molecular_diffusion import (
    MolecularDiffusion,
    MolecularConfig,
    MolecularEnergyField
)

from .plasma_diffusion import (
    PlasmaDiffusion,
    PlasmaConfig,
    PlasmaEnergyField
)

from .enterprise_diffusion import (
    EnterpriseDiffusion,
    EnterpriseConfig,
    EnterpriseEnergyField
)

__all__ = [
    # Molecular domain
    'MolecularDiffusion',
    'MolecularConfig',
    'MolecularEnergyField',

    # Plasma domain
    'PlasmaDiffusion',
    'PlasmaConfig',
    'PlasmaEnergyField',

    # Enterprise domain
    'EnterpriseDiffusion',
    'EnterpriseConfig',
    'EnterpriseEnergyField',
]
